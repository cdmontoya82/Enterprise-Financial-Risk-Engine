# Mathematical Foundations: Pure Monte Carlo vs. Meta Prophet Pipeline

This document provides the formal mathematical and statistical specifications driving the forecasting models implemented in this repository.

---

## 1. Pure Monte Carlo Simulation (Non-Parametric Bootstrapping)

When historical data does not follow a standard theoretical distribution (like Normal or Student-t), we implement a **Non-Parametric Monte Carlo Bootstrap**. Instead of assuming parameters like mean ($\mu$) or variance ($\sigma^2$), the model treats the historical data pool as the empirical distribution of reality.

Let $X = \{x_1, x_2, \dots, x_N\}$ be the universe of clean, aggregated daily historical mileage records.

### The Stochastic Sampling Process
For a forecast horizon of $H = 30$ days, the algorithm draws $H$ independent and identically distributed (i.i.d.) samples from $X$ with replacement. 

For each single simulation scenario $j$ (where $j \in \{1, 2, \dots, 10000\}$):

$$x_{t,j}^* \sim \text{Uniform}(X), \quad \text{for } t = 1, 2, \dots, H$$

The total monthly consolidated kilometers for scenario $j$ is the linear aggregation of these stochastically sampled days:

$$Y_j = \sum_{t=1}^{H} x_{t,j}^*$$

### Risk Percentile Estimation
After generating $M = 10,000$ independent monthly scenarios, we construct the cumulative distribution function (CDF), $F_Y(y)$. The operational risk metrics are extracted using the quantile function $Q(p)$:

$$Q(p) = F_Y^{-1}(p) = \inf \{ y \in \mathbb{R} : F_Y(y) \geq p \}$$

* **Operational Floor (5th Percentile):** $Q(0.05)$, representing a $95\%$ statistical certainty that the monthly mileage will not fall below this threshold.
* **Risk Ceiling (95th Percentile):** $Q(0.95)$, representing the maximum capacity cushion required to cover operational volatility with a $95\%$ confidence level.

---

## 2. Meta Prophet (Additive Time-Series Time Domain Model)

Meta Prophet treats the time-series forecasting problem as a curve-fitting exercise rather than an autoregressive framework (like ARIMA). The macro model is formulated as an additive decomposable time-series equation:

$$y(t) = g(t) + s(t) + h(t) + \epsilon_t$$

Where:
* $g(t)$: **Trend function**, modeling non-periodic structural changes.
* $s(t)$: **Seasonality function**, capturing periodic changes (e.g., weekly cycles, monthly patterns).
* $h(t)$: **Holiday effects**, representing irregular operational disruptions (e.g., festive seasons, national holidays).
* $\epsilon_t$: **Residual error term**, representing unmodeled idiosyncratic white noise.

### A. The Trend Model $g(t)$ (Piecewise Linear with Changepoints)
For logistics operations with structural growth or capacity adjustments, Prophet utilizes a piecewise linear growth model with a selectable number of changepoints $K$:

$$g(t) = (\beta_0 + a(t)^T \delta) \cdot t + (m_0 + a(t)^T \gamma)$$

Where:
* $\beta_0$: Initial growth rate.
* $\delta \in \mathbb{R}^K$: Vector of rate adjustments at specific changepoints $s_k$.
* $a(t) \in \{0, 1\}^K$: An indicator vector such that $a_k(t) = 1$ if $t \geq s_k$.
* $\gamma_k = -s_k \cdot \delta_k$: Parameter configured to ensure the trend function remains structurally continuous.

### B. The Periodic Seasonality $s(t)$ (Fourier Series Decomposition)
To map regular human calendar effects (such as lower freight activity on weekends), seasonal patterns are modeled using a partial sum of a Fourier Series:

$$s(t) = \sum_{n=1}^{N} \left( a_n \cos\left(\frac{2\pi n t}{P}\right) + b_n \sin\left(\frac{2\pi n t}{P}\right) \right)$$

Where:
* $P$: The regular period ($P = 7$ for weekly seasonality, $P = 365.25$ for yearly seasonality).
* $[a_1, b_1, \dots, a_n, b_n]^T$: The structural coefficients estimated by the model using a smoothing prior $\sim \text{Normal}(0, \sigma^2)$. For weekly seasonality, $N=3$ parameters are estimated; for yearly seasonality, $N=10$.
