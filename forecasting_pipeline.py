import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet

# ==============================================================================
# USER CONFIGURATION
# ==============================================================================
TARGET_MONTH = 6      # June
TARGET_YEAR = 2026
NUM_SIMULATIONS = 10000
FORECAST_HORIZON_DAYS = 30
OUTLIER_THRESHOLD_KM = 300000

# ==============================================================================
# 1. DATA LOADING AND PREPROCESSING
# ==============================================================================
def load_and_clean_data(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
        
    # Standardize column types and clean
    df['Kilómetros Reales'] = pd.to_numeric(df['Kilómetros Reales'], errors='coerce')
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.dropna(subset=['Kilómetros Reales', 'Fecha'])
    
    # Extract temporal features for seasonal filtering
    df['Month'] = df['Fecha'].dt.month
    df['Year'] = df['Fecha'].dt.year
    return df

# Create dummy data if file doesn't exist (prevents pipeline crash on Docker test)
file_name = 'Datos_kilometros.csv'
if not os.path.exists(file_name):
    print("Dataset not found. Generating sample structural data for execution...")
    dates = pd.date_range(start="2024-01-01", end="2026-05-31", freq='D')
    base_km = 75000 + (np.sin(np.arange(len(dates)) * (2 * np.pi / 365)) * 10000)
    noise = np.random.normal(0, 5000, len(dates))
    dummy_df = pd.DataFrame({'Fecha': dates, 'Kilómetros Reales': base_km + noise})
    dummy_df.to_csv(file_name, index=False)

df_clean = load_and_clean_data(file_name)

# ==============================================================================
# APPROACH 1: PURE MONTE CARLO SIMULATION (Historical Bootstrapping)
# ==============================================================================
print("Executing Approach 1: Pure Monte Carlo...")
df_seasonal = df_clean[(df_clean['Month'] == TARGET_MONTH) & (df_clean['Year'] == TARGET_YEAR)]

# If historical exact match is empty, fallback to recent 30 days
if df_seasonal.empty:
    df_seasonal = df_clean.tail(30)

df_daily_pure = df_seasonal.groupby('Fecha')['Kilómetros Reales'].sum().reset_index()
df_daily_pure = df_daily_pure[df_daily_pure['Kilómetros Reales'] < OUTLIER_THRESHOLD_KM]

pure_historical_pool = df_daily_pure['Kilómetros Reales'].values
np.random.seed(42)

pure_mc_results = np.array([
    np.sum(np.random.choice(pure_historical_pool, size=FORECAST_HORIZON_DAYS, replace=True))
    for _ in range(NUM_SIMULATIONS)
])

# ==============================================================================
# APPROACH 2: HYBRID MODEL (Prophet Trend + Monte Carlo Residuals)
# ==============================================================================
print("Executing Approach 2: Hybrid Prophet + Monte Carlo Pipeline...")
df_global_daily = df_clean.groupby('Fecha')['Kilómetros Reales'].sum().reset_index()
df_global_daily = df_global_daily[df_global_daily['Kilómetros Reales'] < OUTLIER_THRESHOLD_KM]

# Format specifically for Prophet API
df_prophet = df_global_daily.rename(columns={'Fecha': 'ds', 'Kilómetros Reales': 'y'})

# Fit Prophet Model
model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
model.fit(df_prophet)

# Predict future horizon
future_dates = model.make_future_dataframe(periods=FORECAST_HORIZON_DAYS, freq='D')
forecast = model.predict(future_dates)

# Isolate structural forecast and calculate past residuals (unmodeled chaos)
past_predictions = forecast.iloc[:-FORECAST_HORIZON_DAYS]
residuals = df_prophet['y'].values - past_predictions['yhat'].values
future_structural_base = forecast.tail(FORECAST_HORIZON_DAYS)['yhat'].values

# Simulate risk over structural trend
hybrid_results = np.array([
    np.sum(future_structural_base + np.random.choice(residuals, size=FORECAST_HORIZON_DAYS, replace=True))
    for _ in range(NUM_SIMULATIONS)
])

# ==============================================================================
# REPORTING & METRICS SUMMARY
# ==============================================================================
print("\n" + "="*50)
print("            STATISTICAL SUMMARY REPORT")
print("="*50)
print(f"Metrics | Pure Monte Carlo | Hybrid (Prophet + MC)")
print(f"Mean    | {np.mean(pure_mc_results):,.2f} km | {np.mean(hybrid_results):,.2f} km")
print(f"P5      | {np.percentile(pure_mc_results, 5):,.2f} km | {np.percentile(hybrid_results, 5):,.2f} km")
print(f"P50     | {np.percentile(pure_mc_results, 50):,.2f} km | {np.percentile(hybrid_results, 50):,.2f} km")
print(f"P95     | {np.percentile(pure_mc_results, 95):,.2f} km | {np.percentile(hybrid_results, 95):,.2f} km")
print("="*50)

# ==============================================================================
# ARTIFACT GENERATION (Saves charts for GitHub README)
# ==============================================================================
print("\nGenerating charts for repository documentation...")

# 1. Pure Monte Carlo Chart
plt.figure(figsize=(10, 6))
plt.hist(pure_mc_results, bins=50, color='#3498db', edgecolor='black', alpha=0.7)
plt.axvline(np.percentile(pure_mc_results, 95), color='#e74c3c', linestyle='dashed', linewidth=2, label=f'P95 Ceiling: {np.percentile(pure_mc_results, 95):,.0f} km')
plt.title('Pure Monte Carlo Simulation: Operational Risk Distribution', fontsize=14, fontweight='bold')
plt.xlabel('Total Monthly Kilometers')
plt.ylabel('Frequency (Out of 10,000 simulations)')
plt.legend()
plt.grid(alpha=0.3)
plt.savefig('monte_carlo_pure.png', bbox_inches='tight', dpi=150)
plt.close()

# 2. Hybrid Model Chart
plt.figure(figsize=(10, 6))
plt.hist(hybrid_results, bins=50, color='#2ecc71', edgecolor='black', alpha=0.7)
plt.axvline(np.percentile(hybrid_results, 95), color='#e74c3c', linestyle='dashed', linewidth=2, label=f'P95 Ceiling: {np.percentile(hybrid_results, 95):,.0f} km')
plt.title('Hybrid Prophet + MC Simulation: Compressed Risk Distribution', fontsize=14, fontweight='bold')
plt.xlabel('Total Monthly Kilometers')
plt.ylabel('Frequency (Out of 10,000 simulations)')
plt.legend()
plt.grid(alpha=0.3)
plt.savefig('prophet_monte_carlo_hybrid.png', bbox_inches='tight', dpi=150)
plt.close()

print("Execution complete. Artifacts 'monte_carlo_pure.png' and 'prophet_monte_carlo_hybrid.png' saved successfully.")
