import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from datetime import datetime, timedelta
import matplotlib.patches as patches

# Parameters
current_price = 94.64
strike_price = 100.00
expiry_date = '2024-09-20'
option_price = 0.45
implied_volatility = 13.711 / 100
contracts = 1

# Dates
start_date = datetime.strptime('2024-07-31', '%Y-%m-%d')
expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')
days_to_expiry = (expiry_date - start_date).days
dates = pd.date_range(start=start_date, end=expiry_date)

# Stock price range
price_range = np.arange(93.00, 101.00, 0.33)

# Black-Scholes Formula
def black_scholes_call(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = (S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2))
    return call_price

# Simulation
results = []
risk_free_rate = 0.01  # Assuming a risk-free rate of 1%

for current_date in dates:
    T = (expiry_date - current_date).days / 365
    row = []
    for price in price_range:
        call_price = black_scholes_call(price, strike_price, T, risk_free_rate, implied_volatility)
        profit = (call_price - option_price) * 100 * contracts
        row.append(profit)
    results.append(row)

# Create DataFrame
results_df = pd.DataFrame(results, columns=price_range, index=dates)

# Plotting the heatmap
fig, ax = plt.subplots(figsize=(16, 9))

# Create the heatmap
cax = ax.imshow(results_df.T, aspect='auto', cmap='RdYlGn', origin='lower',
                extent=[0, days_to_expiry, price_range.min(), price_range.max()])
cbar = fig.colorbar(cax, label='Profit/Loss ($)')
cbar.ax.tick_params(labelsize=12)

# Set axis labels
ax.set_xlabel('Date', fontsize=12)
ax.xaxis.set_label_position('top')
ax.xaxis.tick_top()
ax.set_ylabel('Stock Price', fontsize=12)

# Set x-ticks and y-ticks
ax.set_xticks(np.arange(0, days_to_expiry+1, 1))
ax.set_xticklabels(results_df.index.strftime('%d'), rotation=90, fontsize=10)
ax.set_yticks(np.arange(price_range.min(), price_range.max()+1, 1))
ax.set_yticklabels(np.arange(price_range.min(), price_range.max()+1, 1), fontsize=10)

# Add month names in a larger box above the group of days
unique_months = results_df.index.strftime('%b').unique()
for i, month in enumerate(unique_months):
    first_day_of_month = results_df.index[results_df.index.strftime('%b') == month][0]
    last_day_of_month = results_df.index[results_df.index.strftime('%b') == month][-1]
    first_day_position = (first_day_of_month - start_date).days
    last_day_position = (last_day_of_month - start_date).days
    
    # Draw the box
    rect = patches.Rectangle((first_day_position, price_range.max()+0.5), last_day_position - first_day_position + 1, 2,
                             linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(rect)
    
    # Add the month name in the center of the box
    ax.text((first_day_position + last_day_position) / 2, price_range.max() + 2, month,
            ha='center', va='center', fontsize=12, fontweight='bold')

# Add annotations for profit/loss values
for i in range(len(price_range)):
    for j in range(len(dates)):
        profit_value = int(results_df.iloc[j, i])
        color = 'white' if profit_value < 0 else 'black'
        ax.text(j, price_range[i], f'{profit_value}', ha='center', va='center', fontsize=6, color=color)

# Adjusting the title position
plt.title('Estimated Returns', fontsize=16, pad=20)
plt.grid(False)
plt.show()
