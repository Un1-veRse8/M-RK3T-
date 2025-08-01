import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Fetch historical data for ^VIX
vix_data = yf.download('^VIX', start='2000-01-01')

# Resample data to weekly frequency, using the last available value in each week
vix_weekly = vix_data['Close'].resample('2W').last()

# Calculate weekly percentage change
vix_weekly_pct_change = vix_weekly.pct_change() * 100

# Find significant weekly declines (e.g., greater than 10%)
significant_weekly_declines = vix_weekly_pct_change[vix_weekly_pct_change < -10]

# Plotting the data
plt.figure(figsize=(14, 8))
plt.plot(vix_weekly_pct_change.index, vix_weekly_pct_change, label='Weekly % Change', color='lightgray')
plt.scatter(significant_weekly_declines.index, significant_weekly_declines, color='red', label='Significant Declines')

# Highlight the most recent historical decline
recent_weekly_decline_index = significant_weekly_declines.index[-1]
recent_weekly_decline_value = significant_weekly_declines.iloc[-1]
plt.scatter(recent_weekly_decline_index, recent_weekly_decline_value, color='blue', s=100, label='Recent Historical Decline')

# Adding titles and labels
plt.title('Historical ^VIX Weekly Declines (2000-Present)', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Weekly % Change', fontsize=12)
plt.axhline(0, color='black', linewidth=0.5)
plt.legend()

# Show the plot
plt.show()
