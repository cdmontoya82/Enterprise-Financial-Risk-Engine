import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# USER CONFIGURATION
# ==============================================================================
TARGET_MONTH = 6       # June
TARGET_YEAR = 2026
NUM_SIMULATIONS = 10000
FORECAST_HORIZON_DAYS = 30
OUTLIER_THRESHOLD_KM = 300000

# 1. LOAD AND CLEAN FREIGHT DATA
file_name = 'Datos_kilometros.csv' if os.path.exists('Datos_kilometros.csv') else 'Datos_kilometros.xlsx'

try:
    df = pd.read_csv(file_name) 
except:
    df = pd.read_excel(file_name)

# Format columns and drop missing values
df['Kilómetros Reales'] = pd.to_numeric(df['Kilómetros Reales'], errors='coerce')
df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
df = df.dropna(subset=['Kilómetros Reales', 'Fecha'])

# Extract temporal features for seasonal bootstrapping
df['Month'] = df['Fecha'].dt.month
df['Year'] = df['Fecha'].dt.year

# Filter by the target historical season
df_seasonal = df[(df['Month'] == TARGET_MONTH) & (df['Year'] == TARGET_YEAR)]

if df_seasonal.empty:
    raise ValueError(f"No historical data found for Month: {TARGET_MONTH}, Year: {TARGET_YEAR}")

# Group by Date to obtain consolidated national daily mileage
df_daily = df_seasonal.groupby('Fecha')['Kilómetros Reales'].sum().reset_index()

# Remove operational data entry outliers/errors
df_daily = df_daily[df_daily['Kilómetros Reales'] < OUTLIER_THRESHOLD_KM]
historical_pool = df_daily['Kilómetros Reales'].values

print(f"--- PURE MONTE CARLO CONFIGURATION ---")
print(f"Historical Baseline: Month {TARGET_MONTH} / Year {TARGET_YEAR}")
print(f"Total valid baseline days found: {len(historical_pool)}")
print(f"Baseline Daily Mean: {np.mean(historical_pool):,.2f} km\n")

# 2. RUN MONTE CARLO SIMULATION (Historical Bootstrapping)
pure_mc_results = []
np.random.seed(42)  # For reproducibility

for _ in range(NUM_SIMULATIONS):
    # Randomly sample 30 operational days from the historical pool (with replacement)
    simulated_month = np.random.choice(historical_pool, size=FORECAST_HORIZON_DAYS, replace=True)
    pure_mc_results.append(np.sum(simulated_month))

pure_mc_results = np.array(pure_mc_results)

# 3. COMPUTE STATISTICAL RISK PERCENTILES
mean_forecast = np.mean(pure_mc_results)
p50_median = np.percentile(pure_mc_results, 50)
p95_ceiling = np.percentile(pure_mc_results, 95)  # Risk ceiling
p5_floor = np.percentile(pure_mc_results, 5)      # Operational floor

print(f"--- SIMULATION RESULTS ---")
print(f"Expected Mean Mileage: {mean_forecast:,.2f} km")
print(f"Median (50% Probability): {p50_median:,.2f} km")
print(f"Risk Ceiling (95th Percentile - High Demand): {p95_ceiling:,.2f} km")
print(f"Operational Floor (5th Percentile - Low Demand): {p5_floor:,.2f} km")

# 4. PLOT AND EXPORT THE PROBABILITY DISTRIBUTION
plt.figure(figsize=(12, 6))
plt.hist(pure_mc_results, bins=50, color='#66bb6a', edgecolor='black', alpha=0.7)
plt.axvline(mean_forecast, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_forecast:,.0f} km')
plt.axvline(p95_ceiling, color='darkred', linestyle=':', linewidth=2, label=f'95th Percentile: {p95_ceiling:,.0f} km')
plt.axvline(p5_floor, color='blue', linestyle=':', linewidth=2, label=f'5th Percentile: {p5_floor:,.0f} km')

plt.title(f'Monte Carlo Simulation: Monthly Mileage Projection (Base Month: {TARGET_MONTH}-{TARGET_YEAR})', fontsize=14, fontweight='bold')
plt.xlabel('Total Monthly Kilometers Proclaimed', fontsize=12)
plt.ylabel('Frequency (Scenarios Generated)', fontsize=12)
plt.legend(loc='upper right')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()

# Save image for your GitHub README documentation
plt.savefig('monte_carlo_pure.png', dpi=150)
plt.show()
