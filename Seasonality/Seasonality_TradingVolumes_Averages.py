import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# User inputs for stock symbol and number of years back to analyze
symbol = input("Enter the stock symbol (e.g., 'SPY' for S&P 500 ETF): ").strip()
years_back = int(input("Enter the number of years back to analyze (e.g., 1, 2, 10,...): "))

# Calculate start and end dates based on user input
end_date = pd.to_datetime('today')
start_date = pd.Timestamp(year=end_date.year - years_back, month=1, day=1)

# Download historical data from Yahoo Finance
data = yf.download(symbol, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

# Check if data is loaded
if data.empty:
    print("No data fetched. Check the stock symbol or network connection.")
else:
    # Extract month from the index
    data['Month'] = data.index.month

    # Group by month, then calculate the average volume for each month across all years
    monthly_avg_volume = data.groupby('Month')['Volume'].mean()

    # Plotting the average monthly volume using a bar chart
    plt.figure(figsize=(10, 6))
    sns.barplot(x=monthly_avg_volume.index, y=monthly_avg_volume.values, palette="viridis")
    plt.title(f'Average Monthly Volume for {symbol} over the past {years_back} years')
    plt.xlabel('Month')
    plt.ylabel('Average Volume')
    plt.xticks(ticks=range(12), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()
