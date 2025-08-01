import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Function to fetch stock data
def fetch_stock_data(tickers, start_date, end_date):
    stock_data = {}
    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
            if not data.empty:
                stock_data[ticker] = data
            else:
                print(f"No data found for {ticker} in the given date range.")
        except Exception as e:
            print(f"Failed to download data for {ticker}: {e}")
    return pd.DataFrame(stock_data)

# Function to calculate 1-day percentage price changes
def calculate_daily_returns(stock_data):
    daily_returns = stock_data.pct_change(fill_method=None).dropna()
    return daily_returns

# Function to plot daily KDEs with S&P 500 performance
def plot_daily_kdes(daily_returns, sp500_returns, days_back):
    dates = daily_returns.index[-days_back:]
    n_days = len(dates)
    
    if n_days == 0:
        print("No data available for the given date range.")
        return
    
    fig, axes = plt.subplots(n_days, 1, figsize=(12, 2 * n_days), sharex=True)
    fig.subplots_adjust(left=0.15, hspace=1.0)  # Adjust left margin and vertical spacing

    for i, date in enumerate(dates):
        daily_changes = daily_returns.loc[date]
        sp500_change = sp500_returns.loc[date].values[0]
        
        color = 'green' if sp500_change > 0 else 'red'
        sns.kdeplot(daily_changes, ax=axes[i], color=color, fill=True)
        
        mean = daily_changes.mean()
        std_dev = daily_changes.std()
        
        axes[i].axvline(mean, color='blue', linestyle='--')
        axes[i].axvline(mean + std_dev, color='orange', linestyle='--')
        axes[i].axvline(mean - std_dev, color='orange', linestyle='--')
        
        axes[i].set_xlim(-0.2, 0.2)
        axes[i].set_yticks([])
        axes[i].set_ylabel('')

        # Place date annotations on the left side of the plot with smaller font and no box
        axes[i].annotate(f"Date: {date.date()}",
                         xy=(-0.01, 0.5), xycoords='axes fraction', fontsize=8,
                         color='black', ha='right', va='center')
    
    plt.xlabel('1-Day % Price Change')
    plt.show()

# Main script
if __name__ == "__main__":
    # Mag 7 names
    mag_7_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA"]
    
    # Prompt user for the number of days back
    days_back = int(input("Enter the number of days back for the plots: "))
    
    # Choose between Mag 7 and all S&P 500 tickers
    use_all_500 = input("Do you want to use all 500 names in the S&P 500 index? (yes/no): ").strip().lower() == 'yes'
    
    if use_all_500:
        sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
        tickers = sp500_tickers
    else:
        tickers = mag_7_tickers

    sp500_ticker = "^GSPC"  # S&P 500 Index
    
    # Define the date range based on user input
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Fetch stock data
    stock_data = fetch_stock_data(tickers, start_date, end_date)
    sp500_data = fetch_stock_data([sp500_ticker], start_date, end_date)

    # Debug: Print shape of the dataframes to check if they have data
    print("Stock data shape:", stock_data.shape)
    print("S&P 500 data shape:", sp500_data.shape)

    # Ensure we have data before proceeding
    if stock_data.empty or sp500_data.empty:
        print("No data available for the given date range.")
    else:
        # Calculate daily returns
        daily_returns = calculate_daily_returns(stock_data)
        sp500_returns = calculate_daily_returns(sp500_data)

        # Debug: Print head of the dataframes to check the data
        print("Daily returns head:\n", daily_returns.head())
        print("S&P 500 returns head:\n", sp500_returns.head())

        # Plot daily KDEs with the date only
        plot_daily_kdes(daily_returns, sp500_returns, days_back)
