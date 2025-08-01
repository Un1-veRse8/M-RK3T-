import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Step 1: Data Collection
def fetch_data(ticker, start_year):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = f"{start_year}-01-01"
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# Step 2: Calculate Daily Returns
def calculate_daily_returns(data):
    data['Daily Return'] = data['Adj Close'].pct_change()
    return data

# Step 3: Measure Volatility
def calculate_rolling_volatility(data, window=21):
    data['Rolling Volatility'] = data['Daily Return'].rolling(window).std() * (252 ** 0.5)
    return data

# Step 4: Identify High and Low Volatility Periods
def identify_volatility_clusters(data):
    high_vol_threshold = data['Rolling Volatility'].quantile(0.75)
    low_vol_threshold = data['Rolling Volatility'].quantile(0.25)
    
    data['Volatility Regime'] = 'Normal'
    data.loc[data['Rolling Volatility'] > high_vol_threshold, 'Volatility Regime'] = 'High'
    data.loc[data['Rolling Volatility'] < low_vol_threshold, 'Volatility Regime'] = 'Low'
    
    return data, high_vol_threshold, low_vol_threshold

# Step 5: Calculate Forward Returns
def calculate_forward_returns(data, periods_list=[5, 10, 21, 63]):
    for periods in periods_list:
        data[f'{periods}d Forward Return'] = data['Adj Close'].pct_change(periods=periods).shift(-periods)
    return data

# Step 6: Visualize Volatility Clusters and Forward Returns
def visualize_volatility_clusters(data, high_vol_threshold, low_vol_threshold):
    plt.figure(figsize=(14, 7))

    # Plot adjusted close price
    plt.subplot(2, 1, 1)
    plt.plot(data['Adj Close'], label='Adjusted Close')
    plt.title('SPY Adjusted Close Price')
    plt.legend()

    # Plot rolling volatility and highlight high/low volatility periods
    plt.subplot(2, 1, 2)
    plt.plot(data['Rolling Volatility'], label='Rolling Volatility')
    plt.axhline(y=high_vol_threshold, color='r', linestyle='--', label='High Volatility Threshold')
    plt.axhline(y=low_vol_threshold, color='g', linestyle='--', label='Low Volatility Threshold')

    # Highlight high volatility periods
    plt.fill_between(data.index, data['Rolling Volatility'], high_vol_threshold, where=(data['Volatility Regime'] == 'High'), color='r', alpha=0.3)

    # Highlight low volatility periods
    plt.fill_between(data.index, data['Rolling Volatility'], low_vol_threshold, where=(data['Volatility Regime'] == 'Low'), color='g', alpha=0.3)

    plt.yscale('log')  # Apply log scale
    plt.title('SPY Rolling Volatility with Clusters (Log Scale)')
    plt.legend()

    plt.tight_layout()
    plt.show()

def visualize_forward_return_scatter_plots(data):
    current_data_point = data.iloc[-1]

    # Scatter plots of rolling volatility vs. forward returns for different periods
    forward_return_periods = [5, 10, 21, 63]
    fig, axes = plt.subplots(2, 2, figsize=(14, 14))
    fig.suptitle('Rolling Volatility vs. Forward Returns', fontsize=16)

    for ax, periods in zip(axes.flatten(), forward_return_periods):
        ax.scatter(data['Rolling Volatility'], data[f'{periods}d Forward Return'], alpha=0.5, label='All Data')
        ax.scatter(current_data_point['Rolling Volatility'], current_data_point[f'{periods}d Forward Return'], color='red', label='Current Data Point')
        ax.annotate(data.index[-1].strftime('%Y-%m-%d'), (current_data_point['Rolling Volatility'], current_data_point[f'{periods}d Forward Return']))
        ax.set_title(f'{periods}-Day Forward Return')
        ax.set_xlabel('Rolling Volatility')
        ax.set_ylabel(f'{periods}d Forward Return')
        ax.legend()

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

# Main Function
def main():
    ticker = "SPY"  # SPDR S&P 500 ETF
    start_year = input("Enter the start year for analysis (e.g., 2000): ")
    
    data = fetch_data(ticker, start_year)
    data = calculate_daily_returns(data)
    data = calculate_rolling_volatility(data)
    data, high_vol_threshold, low_vol_threshold = identify_volatility_clusters(data)
    data = calculate_forward_returns(data)
    
    visualize_volatility_clusters(data, high_vol_threshold, low_vol_threshold)
    visualize_forward_return_scatter_plots(data)

if __name__ == "__main__":
    main()
