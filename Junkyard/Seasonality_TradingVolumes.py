import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# User inputs for stock symbol and number of years back to analyze
symbol = input("Enter the stock symbol (e.g., 'SPY' for S&P 500 ETF): ").strip()
years_back = int(input("Enter the number of years back to analyze (e.g., 1, 2, 10,...): "))

# Calculate start and end dates based on user input
end_date = pd.to_datetime('today')
start_date = end_date - pd.DateOffset(years=years_back)

# Adjust start date to the beginning of the year to ensure coverage of all months
start_date = pd.Timestamp(year=start_date.year, month=1, day=1)

# Download historical data from Yahoo Finance
data = yf.download(symbol, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

# Check if data is loaded
if data.empty:
    print("No data fetched. Check the stock symbol or network connection.")
else:
    # Extract year and month from the index
    data['Year'] = data.index.year
    data['Month'] = data.index.month

    # Group by year and month, then calculate the average volume
    monthly_volume = data.groupby(['Year', 'Month'])['Volume'].mean().unstack()

    # Plotting the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(monthly_volume, annot=True, fmt=".0f", cmap='viridis', linewidths=.5, annot_kws={'size': 4})
    plt.title(f'Average Monthly Volume Heatmap for {symbol} from {start_date.year} to {end_date.year}')
    plt.xlabel('Month')
    plt.ylabel('Year')
    plt.show()
