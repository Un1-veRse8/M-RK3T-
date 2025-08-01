import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf

# Fetch historical data for ^GSPC
symbol = "^GSPC"
data = yf.download(symbol, start="1927-01-01", end="2024-12-20")
data["Month"] = data.index.month
data["Year"] = data.index.year
data["Day"] = data.index.day
data["Daily Return"] = data["Adj Close"].pct_change()

# Monthly Average Returns
data_monthly = data.groupby(["Year", "Month"])['Daily Return'].mean().unstack()
monthly_avg = data_monthly.mean()

# Day-of-Month Seasonality
data_dom = data.groupby(["Month", "Day"])['Daily Return'].mean().unstack()

# Cumulative Return Line Chart
historical_avg = data.groupby(data.index.dayofyear)['Daily Return'].mean().cumsum()
current_year = data[data['Year'] == 2024]
cumulative_current = current_year['Daily Return'].cumsum()

# Plotting
fig, axes = plt.subplots(2, 2, figsize=(15, 12), gridspec_kw={'height_ratios': [1, 2]})

# Heatmap: Monthly Average Returns
monthly_avg_values = monthly_avg.values.reshape(1, -1)  # Reshape to 1 row and 12 columns
sns.heatmap(monthly_avg_values, cmap="RdYlGn", annot=monthly_avg_values, fmt=".2f", cbar=False, ax=axes[0, 0])
axes[0, 0].set_title(f"Seasonality Heatmap of {symbol}")
axes[0, 0].set_xticks(range(12))
axes[0, 0].set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
axes[0, 0].set_yticks([])
axes[0, 0].set_ylabel("Average Monthly Return (%)")

# Heatmap: Day-of-Month Seasonality
sns.heatmap(data_dom, cmap="RdYlGn", cbar=True, ax=axes[0, 1])
axes[0, 1].set_title(f"Day of Month Seasonality for {symbol}")
axes[0, 1].set_ylabel("Day of Month")
axes[0, 1].set_xlabel("Month")

# Line Chart: Historical Average vs Current Year
axes[1, 0].plot(historical_avg.index, historical_avg.values, label="Historical Average", color="blue")
axes[1, 0].plot(cumulative_current.index, cumulative_current.values, label="Year 2024", color="red")
axes[1, 0].axhline(0, color="black", linestyle="--")
axes[1, 0].set_title(f"Seasonality Line Chart of {symbol}")
axes[1, 0].set_xlabel("Day of Year")
axes[1, 0].set_ylabel("Cumulative Return")
axes[1, 0].legend()

# Remove empty subplot
axes[1, 1].axis("off")

# Footer
fig.text(0.5, 0.01, f"Data from 1927-01-01 to 2024-12-20", ha="center", fontsize=10)

plt.tight_layout()
plt.show()
