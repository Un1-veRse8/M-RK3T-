import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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

# Function to calculate daily returns
def calculate_daily_returns(stock_data):
    daily_returns = stock_data.pct_change(fill_method=None).dropna()
    return daily_returns

# Function to plot heatmap of daily returns
def plot_daily_returns_heatmap(daily_returns):
    plt.figure(figsize=(14, 10))
    sns.heatmap(daily_returns.T, cmap='coolwarm', cbar_kws={'label': 'Daily Return'})
    plt.title('Heatmap of Daily Returns')
    plt.xlabel('Date')
    plt.ylabel('Stocks')
    plt.show()

# Main script
if __name__ == "__main__":
    # Fetch list of S&P 500 tickers
    sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
    
    # Prompt user for the number of years back
    years_back = int(input("Enter the number of years back for the heatmap: "))
    
    # Define the date range based on user input
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years_back * 365)
    
    # Fetch stock data
    stock_data = fetch_stock_data(sp500_tickers, start_date, end_date)
    
    if stock_data.empty:
        print("No data available for the given date range.")
    else:
        # Calculate daily returns
        daily_returns = calculate_daily_returns(stock_data)
        
        # Plot heatmap of daily returns
        plot_daily_returns_heatmap(daily_returns)
