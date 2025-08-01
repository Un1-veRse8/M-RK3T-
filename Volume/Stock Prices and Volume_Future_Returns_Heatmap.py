import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

# User input for stock symbol and years back to analyze
symbol = input("Enter the stock symbol (e.g., 'AAPL'): ").strip()
years_back = int(input("Enter the number of years back to analyze (e.g., 1, 2, 3,...): "))

# Calculate start and end dates
end_date = datetime.now()
start_date = end_date - timedelta(days=365 * years_back)

# Download historical data
data = yf.download(symbol, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

# Ensure data is loaded
if data.empty:
    print("No data fetched. Check the stock symbol or network connection.")
else:
    # Calculate daily returns
    data['Daily Return'] = data['Adj Close'].pct_change() * 100

    # Define forecast periods
    forecast_days = [5, 10, 21, 63, 126, 252]

    # Calculate future returns
    for days in forecast_days:
        data[f'Return_{days}_days'] = data['Adj Close'].shift(-days) / data['Adj Close'] - 1

    # Drop rows with NaN values in future returns
    data.dropna(subset=[f'Return_{days}_days' for days in forecast_days], inplace=True)

    # Plotting scatter plots
    fig, axes = plt.subplots(3, 2, figsize=(14, 18))
    axes = axes.flatten()
    for i, days in enumerate(forecast_days):
        axes[i].scatter(data['Volume'], data[f'Return_{days}_days'], alpha=0.5)
        axes[i].set_title(f'{symbol} - Volume vs Return {days} Days Later')
        axes[i].set_xlabel('Volume')
        axes[i].set_ylabel(f'Return After {days} Days (%)')
        axes[i].grid(True)

        # Linear regression
        X = data['Volume'].values.reshape(-1, 1)
        y = data[f'Return_{days}_days'].values
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        axes[i].plot(data['Volume'], y_pred, color='red', linewidth=2, label='Regression Line')
        axes[i].legend()

        # Adding a text watermark to each subplot
        axes[i].text(0.5, 0.5, 'o5341V', fontsize=20, color='gray', ha='center', va='center', alpha=0.5, transform=axes[i].transAxes)

    fig.tight_layout(pad=2.0)
    plt.show()

print("https://twitter.com/o5341V")
