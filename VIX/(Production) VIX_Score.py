import yfinance as yf
import pandas as pd
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

# Fetch historical data for ^VIX
vix_data = yf.download('^VIX', start='1990-01-01')
vix_data.dropna(subset=['Close'], inplace=True)

# Closing prices
close_prices = vix_data['Close']
current_price = close_prices.iloc[-1]

# Statistical calculations
mean_vix_price = close_prices.mean()
median_vix_price = close_prices.median()
std_dev_vix_price = close_prices.std()
percentile_rank = stats.percentileofscore(close_prices, current_price)
z_score = (current_price - mean_vix_price) / std_dev_vix_price

# Rolling metrics
rolling_mean_21 = close_prices.rolling(21).mean().iloc[-1]
rolling_std_21 = close_prices.rolling(21).std().iloc[-1]
rolling_z_score = (current_price - rolling_mean_21) / rolling_std_21

# Mean reversion factor
mean_reversion_factor = abs(current_price - mean_vix_price) / std_dev_vix_price

# Stress-level comparisons
stress_events = {
    "2008 Crisis": 80,
    "COVID-19": 82,
    "Dot-com Bubble": 77
}
stress_adjusted_score = max(
    [100 - abs(percentile_rank - level) for level in stress_events.values()]
)

# Confidence interval
ci_lower = mean_vix_price - 1.0 * std_dev_vix_price
ci_upper = mean_vix_price + 2.0 * std_dev_vix_price
outside_ci_penalty = 0
if current_price < ci_lower or current_price > ci_upper:
    outside_ci_penalty = -10

# Sharpe-like ratio
vix_sharpe_ratio = (mean_vix_price - current_price) / std_dev_vix_price

# Composite score weights
if current_price > 25:  # High volatility
    w1, w2, w3, w4, w5 = 0.3, 0.5, 0.1, 0.1, 0
elif current_price < 15:  # Low volatility
    w1, w2, w3, w4, w5 = 0.5, 0.3, 0.1, 0.1, 0
else:  # Moderate volatility
    w1, w2, w3, w4, w5 = 0.4, 0.4, 0.1, 0.1, 0

# Composite score calculation
composite_score = (
    w1 * (100 - percentile_rank) +
    w2 * max(1 - abs(z_score), 0) * 100 +
    w3 * (1 / (1 + mean_reversion_factor)) * 100 +
    w4 * stress_adjusted_score +
    w5 * vix_sharpe_ratio * 10 +
    outside_ci_penalty
)

# Above 70: Strong undervaluation. Likely a good time to hedge or expect a reversion upward.
# 40-70: Fairly valued. No significant signal for action.
# Below 40: Overvaluation. Market may be pricing in extreme fear or complacency.

# Display results
print(f"Current VIX closing price: {current_price:.2f}")
#print(f"Mean closing price: {mean_vix_price:.2f}")
#print(f"Median closing price: {median_vix_price:.2f}")
#print(f"Standard deviation: {std_dev_vix_price:.2f}")
#print(f"Percentile rank of current price: {percentile_rank:.2f}%")
#print(f"Z-Score of current price: {z_score:.2f}")
#print(f"Rolling mean (21-day): {rolling_mean_21:.2f}")
#print(f"Rolling Z-Score (21-day): {rolling_z_score:.2f}")
#print(f"Mean reversion factor: {mean_reversion_factor:.2f}")
#print(f"Stress-adjusted score: {stress_adjusted_score:.2f}")
#print(f"95% Confidence Interval: {ci_lower:.2f} to {ci_upper:.2f}")
##print(f"Sharpe-like ratio: {vix_sharpe_ratio:.2f}")
print(f"Composite value score: {composite_score:.2f}")

