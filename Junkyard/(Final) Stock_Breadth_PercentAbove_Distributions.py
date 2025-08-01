import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import tkinter as tk

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

# Function to center the plot window on the screen using tkinter
def center_window(width=800, height=600):
    root = tk.Tk()
    root.withdraw()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.destroy()
    return x, y, width, height

# Function to plot the probability distributions
def plot_probability_distributions(percentages, current_values, x_increment):
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    ma_labels = ['20-Day MA', '50-Day MA', '100-Day MA', '200-Day MA']
    colors = ['blue', 'blue', 'blue', 'blue']  # All plots blue

    axs = axs.flatten()
    for i, (label, percentage) in enumerate(percentages.items()):
        ax = axs[i]
        filtered_percentage = percentage[percentage > 0]  # Filter out 0 values
        n, bins, patches = ax.hist(filtered_percentage, bins=50, alpha=0.7, color=colors[i], edgecolor='black')
        current_bin = int(current_values[i] // (100 / 50))
        if current_bin < len(patches):
            patches[current_bin].set_facecolor('yellow')
        ax.set_xlabel('Percentage')
        ax.set_ylabel('Frequency')
        ax.set_xticks(range(0, 101, x_increment))  # Set x-axis increments based on user input
        ax.legend([f'Stocks Above {ma_labels[i]} Distribution', 'Current Value Highlighted'], loc='upper left')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Center the plot window
    x, y, width, height = center_window(1200, 800)
    manager = plt.get_current_fig_manager()
    manager.window.wm_geometry(f"{width}x{height}+{x}+{y}")

    plt.show()

# Main script
if __name__ == "__main__":
    # Fetch list of S&P 500 tickers
    sp500_table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    sp500_tickers = sp500_table['Symbol'].tolist()
    
    # Prompt user to choose between top 100 by market cap or all 500 components
    choice = input("Enter '100' to analyze top 100 components by market cap or '500' to analyze all 500 components: ").strip()

    if choice == '100':
        # Fetch market cap data
        market_caps = []
        for ticker in sp500_tickers:
            try:
                market_cap = yf.Ticker(ticker).info['marketCap']
                market_caps.append((ticker, market_cap))
            except:
                market_caps.append((ticker, 0))
        
        # Sort by market cap and select top 100
        top_100_tickers = [x[0] for x in sorted(market_caps, key=lambda x: x[1], reverse=True)[:100]]
        tickers_to_analyze = top_100_tickers
    else:
        tickers_to_analyze = sp500_tickers
    
    # Define the date range based on the maximum available data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 14)  # Fetch data for the last 10 years
    
    # Fetch stock data
    stock_data = fetch_stock_data(tickers_to_analyze, start_date, end_date)
    sp500_data = yf.download('^GSPC', start=start_date, end=end_date)['Adj Close']
    
    if stock_data.empty or sp500_data.empty:
        print("No data available for the given date range.")
    else:
        # Calculate moving averages
        ma_200 = calculate_moving_averages(stock_data, 200)
        ma_100 = calculate_moving_averages(stock_data, 100)
        ma_50 = calculate_moving_averages(stock_data, 50)
        ma_20 = calculate_moving_averages(stock_data, 20)
        
        # Calculate percentage of stocks above moving averages
        perc_above_200 = calculate_percentage_above_ma(stock_data, ma_200)
        perc_above_100 = calculate_percentage_above_ma(stock_data, ma_100)
        perc_above_50 = calculate_percentage_above_ma(stock_data, ma_50)
        perc_above_20 = calculate_percentage_above_ma(stock_data, ma_20)
        
        # Get the current percentages
        current_values = [
            perc_above_20.iloc[-1],
            perc_above_50.iloc[-1],
            perc_above_100.iloc[-1],
            perc_above_200.iloc[-1]
        ]
        
        # Prompt user for the x-axis increment
        x_increment = int(input("Enter the increment for the x-axis percentages (e.g., 5): "))
        
        # Plot the probability distributions
        percentages = {
            '20-Day MA': perc_above_20,
            '50-Day MA': perc_above_50,
            '100-Day MA': perc_above_100,
            '200-Day MA': perc_above_200
        }
        plot_probability_distributions(percentages, current_values, x_increment)