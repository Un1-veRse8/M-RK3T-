import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
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
    # Calculate daily returns as percentage
    data['Daily Return'] = data['Adj Close'].pct_change() * 100  # Multiplying by 100 to convert to percentage

    data['Volume (Millions)'] = data['Volume'] / 1e6  # Normalize volume for readability

    # Define forecast periods
    forecast_days = [5, 10, 21, 63, 126, 252]

    # Calculate future returns for specified forecast days
    for days in forecast_days:
        data[f'Return_{days}_days'] = (data['Adj Close'].shift(-days) / data['Adj Close'] - 1) * 100

    # Dropping rows where any forecast return is NaN
    output_data = data[['Volume (Millions)', 'Daily Return'] + [f'Return_{days}_days' for days in forecast_days]].dropna()

    # Define the directory path where you want to save the file
    directory_path = "C:/Users/seana/OneDrive/Desktop/Volume_FutureReturns"  # Adjust to your directory

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)  # Create the directory if it does not exist

    # Save to CSV
    csv_file_path = os.path.join(directory_path, f"{symbol}_future_returns.csv")
    output_data.to_csv(csv_file_path, index=True)
    print(f"Data saved to {csv_file_path}")
