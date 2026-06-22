Mathematical Foundations: Pure Monte Carlo vs. Meta Prophet Pipeline

This document provides the formal mathematical and statistical specifications driving the forecasting models implemented in this repository.
1. Pure Monte Carlo Simulation (Non-Parametric Bootstrapping)

When historical data does not follow a standard theoretical distribution (like Normal or Student-t), we implement a Non-Parametric Monte Carlo Bootstrap. Instead of assuming parameters like mean (μ) or variance (σ2), the model treats the historical data pool as the empirical distribution of reality.

Let X={x1​,x2​,…,xN​} be the universe of clean, aggregated daily historical mileage records.
The Stochastic Sampling Process

For a forecast horizon of H=30 days, the algorithm draws H independent and identically distributed (i.i.d.) samples from X with replacement.

For each single simulation scenario j (where j∈{1,2,…,10000}):
xt,j∗​∼Uniform(X),for t=1,2,…,H

The total monthly consolidated kilometers for scenario j is the linear aggregation of these stochastically sampled days:
Yj​=t=1∑H​xt,j∗​
Risk Percentile Estimation

After generating M=10,000 independent monthly scenarios, we construct the cumulative distribution function (CDF), FY​(y). The operational risk metrics are extracted using the quantile function Q(p):
Q(p)=FY−1​(p)=inf{y∈R:FY​(y)≥p}

    Operational Floor (5th Percentile): Q(0.05), representing a 95% statistical certainty that the monthly mileage will not fall below this threshold.

    Risk Ceiling (95th Percentile): Q(0.95), representing the maximum capacity cushion required to cover operational volatility with a 95% confidence level.

2. Meta Prophet (Additive Time-Series Time Domain Model)

Meta Prophet treats the time-series forecasting problem as a curve-fitting exercise rather than an autoregressive framework (like ARIMA). The macro model is formulated as an additive decomposable time-series equation:
y(t)=g(t)+s(t)+h(t)+ϵt​

Where:

    g(t): Trend function, modeling non-periodic structural changes.

    s(t): Seasonality function, capturing periodic changes (e.g., weekly cycles, monthly patterns).

    h(t): Holiday effects, representing irregular operational disruptions (e.g., festive seasons, national holidays).

    ϵt​: Residual error term, representing unmodeled idiosyncratic white noise.

A. The Trend Model g(t) (Piecewise Linear with Changepoints)

For logistics operations with structural growth or capacity adjustments, Prophet utilizes a piecewise linear growth model with a selectable number of changepoints K:
g(t)=(β0​+a(t)Tδ)⋅t+(m0​+a(t)Tγ)

Where:

    β0​: Initial growth rate.

    δ∈RK: Vector of rate adjustments at specific changepoints sk​.

    a(t)∈{0,1}K: An indicator vector such that ak​(t)=1 if t≥sk​.

    γk​=−sk​⋅δk​: Parameter configured to ensure the trend function remains structurally continuous.

B. The Periodic Seasonality s(t) (Fourier Series Decomposition)

To map regular human calendar effects (such as lower freight activity on weekends), seasonal patterns are modeled using a partial sum of a Fourier Series:
s(t)=n=1∑N​(an​cos(P2πnt​)+bn​sin(P2πnt​))

Where:

    P: The regular period (P=7 for weekly seasonality, P=365.25 for yearly seasonality).

    [a1​,b1​,…,an​,bn​]T: The structural coefficients estimated by the model using a smoothing prior ∼Normal(0,σ2). For weekly seasonality, N=3 parameters are estimated; for yearly seasonality, N=10.

3. The Hybrid Integration Logic (Residual Risk Simulation)

The true power of this data product lies in combining both frameworks to isolate predictive structure from purely stochastic volatility.
Step 1: Deterministic Extrapolation

Prophet extracts the structural component y^​(t) for the next H days, locking in the calendar trends (weekends, holiday impacts):
y^​(t)=g(t)+s(t)+h(t)
Step 2: Extracting the Pure Chaos Vector (Residuals)

We calculate the empirical distribution of unmodeled operational noise R from historical data matching:
R={ϵτ​=y(τ)−y^​(τ)∀τ∈History}
Step 3: Hybrid Stochastic Projection

Instead of simulating raw historical data, the Monte Carlo engine acts directly on the residual vector R. For each simulation scenario j:
Yjhybrid​=t=1∑H​(y^​(t)+ϵt,j∗​),where ϵt,j∗​∼Uniform(R)
The Variance Compression Proof

By removing the calendar structural components (g(t),s(t)) from the data pool prior to Monte Carlo resampling, the variance of the error pool is strictly lower than the variance of the raw historical pool:
Var(R)<Var(X)

This mathematical inequality explains why the Hybrid Model bell curve is significantly narrower and more precise than the Pure Monte Carlo distribution, optimizing financial risk management without over-budgeting.
