import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
from scipy.stats import norm

def calculate_option_price(S, X, T, sigma, option_type='call'):
    """
    Calculate the Black-Scholes option price and theta.

    :param S: Current stock price
    :param X: Strike price
    :param T: Time to expiration in years
    :param sigma: Implied volatility
    :param option_type: 'call' for call option, 'put' for put option
    :return: Option price and theta
    """
    d1 = (math.log(S / X) + (0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if option_type == 'call':
        price = S * norm.cdf(d1) - X * norm.cdf(d2)
        theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T))) / 365
    elif option_type == 'put':
        price = X * norm.cdf(-d2) - S * norm.cdf(-d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T))) / 365
    else:
        raise ValueError("Option type must be 'call' or 'put'")
    
    return price, theta

# User inputs
S = 14.64  # Current stock price
X = 15  # Strike price
sigma = 0.22  # Implied volatility as a percentage
T_days = 233  # Time to expiration in days
option_type = 'call'  # Option type ('call' or 'put')

# Convert time to expiration from days to years
T = T_days / 365.0

# Price changes and time periods to generate heatmap data
price_changes = np.arange(S - 10, S + 10.1, 0.1)  # More granular price changes
time_periods = np.arange(0, T_days + 1, 10)  # Time periods in 10-day intervals

# Calculate initial option price and theta
initial_option_price, theta = calculate_option_price(S, X, T, sigma, option_type)

# Calculate breakeven price
if option_type == 'call':
    breakeven_price = X + initial_option_price
elif option_type == 'put':
    breakeven_price = X - initial_option_price

# Generate heatmap data
heatmap_data = np.zeros((len(price_changes), len(time_periods)))

for i, price_change in enumerate(price_changes):
    for j, time_period in enumerate(time_periods):
        T_remaining = (T_days - time_period) / 365.0
        if T_remaining <= 0:
            option_price = 0  # Option has expired
        else:
            new_underlying_price = price_change
            new_option_price, _ = calculate_option_price(new_underlying_price, X, T_remaining, sigma, option_type)
            option_price_with_theta = new_option_price + theta * time_period
            heatmap_data[i, j] = option_price_with_theta

# Create the heatmap
plt.figure(figsize=(14, 8))
sns.heatmap(heatmap_data, annot=False, fmt=".2f", xticklabels=time_periods, yticklabels=np.round(price_changes, 2), cmap='RdYlGn', cbar_kws={'label': 'Option Price'})
plt.xlabel('Days to Expiration')
plt.ylabel('Underlying Price')
plt.title(f'Estimated Option Prices Over Time and Price Changes (Breakeven Price: {breakeven_price:.2f})')
plt.show()
