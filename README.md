# Corporate Financial Risk Engine & Monte Carlo Simulator

This repository contains an end-to-end analytical data pipeline designed to model corporate financial uncertainty and estimate the **Value at Risk (VaR)** of operating cash flows using **Monte Carlo Simulations**. 

## 📊 Business Problem
Traditional financial projections rely on linear, static assumptions (e.g., assuming a fixed 5% annual growth). However, macroeconomic shifts, logistics anomalies, inflation, and volatile freight prices create high operational uncertainty. This engine substitutes static numbers with stochastic distributions, computing **10,000 parallel market scenarios** to safeguard corporate liquidity.

## 🛠️ Architecture & Tech Stack
- **Python Core:** Built without unnecessary heavy frameworks using standard computational libraries (`NumPy`, `Pandas`).
- **Data Engineering (Storage Optimization):** The simulator outputs dense, multi-variable data rows. To demonstrate modern corporate governance and pipeline optimization, results are compressed and stored utilizing **Apache Parquet (`pyarrow`)**, ensuring lightweight storage and high-throughput reading.
- **Quantitative Finance:** Implements Probability Distributions (Gaussian/Normal) to inject cost and revenue shocks, establishing risk boundaries using the 95th percentile threshold.

## 📂 Project Structure
- `financial_simulation.py`: The core pipeline execution script. Generates the stochastic matrix, executes the simulations, calculates the VaR metrics, and exports the optimized data lake file.
- `monte_carlo_financial_results.parquet`: The high-performance snapshot of the simulation results.

## 📈 Executive Risk Report
When executed, the system evaluates the cumulative performance across all parallel universes, yielding critical KPIs for financial controllers:
- **Expected Net Cash Flow:** The statistical mean of the company's financial generation.
- **Value at Risk (VaR at 95% Confidence):** The ultimate risk-management baseline. It establishes the worst-case scenario with a 95% level of confidence, ensuring strategic alignment for dynamic pricing models.

---
*Developed as a showcase of Financial Analytics & Full-Stack Data Science integration.*
