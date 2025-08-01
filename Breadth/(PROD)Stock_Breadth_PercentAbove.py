import yfinance as yf
import pandas as pd
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

# Function to calculate moving averages
def calculate_moving_averages(stock_data, window):
    return stock_data.rolling(window=window).mean()

# Function to calculate percentage of stocks above moving average
def calculate_percentage_above_ma(stock_data, moving_avg):
    return (stock_data > moving_avg).mean(axis=1) * 100

# Function to plot percentage of stocks above moving averages
def plot_percentage_above_ma(dates, percentages, sp500_data, title):
    plt.figure(figsize=(14, 8))
    
    # Plot S&P 500 index on a logarithmic scale
    plt.subplot(2, 1, 1)
    plt.plot(sp500_data.index, sp500_data, label='S&P 500 Index')
    plt.yscale('log')
    plt.title('S&P 500 Index (Log Scale)')
    plt.xlabel('Date')
    plt.ylabel('S&P 500 Index Level')
    plt.legend()
    
    # Plot percentages
    plt.subplot(2, 1, 2)
    for label, data in percentages.items():
        plt.plot(dates, data, label=label)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Percentage of Stocks Above MA')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

# Main script
if __name__ == "__main__":
    # Fetch list of S&P 500 tickers
    sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
    
    # Prompt user for the number of years back
    years_back = int(input("Enter the number of years back for the plots: "))
    
    # Define the date range based on user input
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years_back * 365)
    
    # Fetch stock data
    stock_data = fetch_stock_data(sp500_tickers, start_date, end_date)
    sp500_data = yf.download('^GSPC', start=start_date, end=end_date)['Adj Close']
    
    if stock_data.empty or sp500_data.empty:
        print("No data available for the given date range.")
    else:
        # Calculate moving averages
        ma_252 = calculate_moving_averages(stock_data, 200)
        ma_52 = calculate_moving_averages(stock_data, 50)
        ma_21 = calculate_moving_averages(stock_data, 21)
        
        # Calculate percentage of stocks above moving averages
        perc_above_252 = calculate_percentage_above_ma(stock_data, ma_252)
        perc_above_52 = calculate_percentage_above_ma(stock_data, ma_52)
        perc_above_21 = calculate_percentage_above_ma(stock_data, ma_21)
        
        # Prompt user for which moving averages to display
        ma_options = input("Enter the moving averages to display (252, 52, 21, or all): ").strip().lower()
        
        percentages = {}
        if ma_options in ['252', 'all']:
            percentages['Above 252 MA'] = perc_above_252
        if ma_options in ['52', 'all']:
            percentages['Above 52 MA'] = perc_above_52
        if ma_options in ['21', 'all']:
            percentages['Above 21 MA'] = perc_above_21
        
        # Plot percentages and S&P 500 index
        plot_percentage_above_ma(stock_data.index, percentages, sp500_data, 'Percentage of Stocks Above Moving Averages')
