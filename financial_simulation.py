import os
import numpy as np
import pandas as pd

def run_corporate_monte_carlo(simulations=10000, months=12):
    """
    Simula el Flujo de Caja Operativo e inyecta volatilidad en costos y ventas
    usando el Método de Monte Carlo para calcular el riesgo financiero (VaR).
    """
    print(f"[*] Iniciando simulación de Monte Carlo con {simulations} escenarios a {months} meses...")
    
    # Parámetros financieros base (Mensuales)
    base_revenue = 150000       # Ingresos esperados base
    revenue_volatility = 0.08   # Volatilidad del mercado en ventas (8%)
    
    base_costs = 95000          # Costos operativos base (Logística, nómina, insumos)
    costs_volatility = 0.12     # Volatilidad en costos (12% por inflación/fletes)
    
    fixed_taxes_rate = 0.30     # Impuestos y tasas fijas (30%)
    
    all_scenarios = []
    
    # Correr las simulaciones
    for sim_id in range(simulations):
        # Generar variaciones aleatorias distribuidas normalmente para el año completo
        rev_samples = np.random.normal(base_revenue, base_revenue * revenue_volatility, months)
        cost_samples = np.random.normal(base_costs, base_costs * costs_volatility, months)
        
        for month in range(months):
            rev = max(0, rev_samples[month]) # Evitar ingresos negativos absolutos
            costs = max(0, cost_samples[month])
            
            ebitda = rev - costs
            taxes = max(0, ebitda * fixed_taxes_rate)
            net_cash_flow = ebitda - taxes
            
            all_scenarios.append({
                "Simulation_ID": sim_id,
                "Month": month + 1,
                "Revenue": round(rev, 2),
                "Operating_Costs": round(costs, 2),
                "EBITDA": round(ebitda, 2),
                "Net_Cash_Flow": round(net_cash_flow, 2)
            })
            
    df = pd.DataFrame(all_scenarios)
    
    # 2. DATA ENGINEERING: Optimización de almacenamiento con Apache Parquet
    output_filename = "monte_carlo_financial_results.parquet"
    print(f"[*] Optimizando datos. Guardando {len(df)} registros en formato Apache Parquet...")
    df.to_parquet(output_filename, engine="pyarrow", compression="snappy")
    
    # 3. ANÁLISIS CORPORATIVO AVANZADO: Métricas de Riesgo (Value at Risk - VaR)
    # Agrupamos por simulación para evaluar el flujo neto total acumulado en el periodo
    total_flow_per_sim = df.groupby("Simulation_ID")["Net_Cash_Flow"].sum()
    
    expected_value = total_flow_per_sim.mean()
    var_95 = np.percentile(total_flow_per_sim, 5) # Percentil 5 (Peor 5% de los escenarios)
    
    print("\n" + "="*50)
    print("📈 INFORME EJECUTIVO DE RIESGO FINANCIERO")
    print("="*50)
    print(f"Flujo Neto Total Esperado (Promedio):   ${expected_value:,.2f}")
    print(f"Value at Risk (VaR 95% de Confianza):  ${var_95:,.2f}")
    print(f"Explicación: Bajo condiciones de extrema volatilidad, existe un 95% ")
    print(f"de certeza de que el Flujo Neto NO caerá por debajo de ${var_95:,.2f}.")
    print("="*50 + "\n")
    
    return df

if __name__ == "__main__":
    df_results = run_corporate_monte_carlo()
