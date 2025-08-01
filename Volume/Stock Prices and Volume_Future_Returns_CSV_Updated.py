import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os

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
    # Calculate daily returns to be used as baseline for calculations
    data['Daily Return'] = data['Adj Close'].pct_change()
    data['Volume (Millions)'] = data['Volume'] / 1e6  # Normalize volume for readability

    # Define forecast periods
    forecast_days = [5, 10, 21, 63, 126, 252]

    # Calculate future returns for specified forecast days
    for days in forecast_days:
        data[f'Return_{days}_days'] = (data['Adj Close'].shift(-days) / data['Adj Close'] - 1) * 100

    # Define bins for volume
    volume_bins = pd.qcut(data['Volume (Millions)'], q=5, duplicates='drop')  # Create 5 quantile-based bins

    # Group by bins and calculate average returns for each bin
    bin_group = data.groupby(volume_bins)
    average_returns = bin_group[[f'Return_{days}_days' for days in forecast_days]].mean()

    # Print average returns for each volume bin
    print(average_returns)

    # Optionally, save to CSV
    csv_file_path = f"{symbol}_binned_future_returns.csv"
    average_returns.to_csv(csv_file_path, index=True)
    print(f"Averaged data saved to {csv_file_path}")
