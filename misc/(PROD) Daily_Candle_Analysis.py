import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Step 1: Data Collection
def fetch_data(ticker, start_year):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = f"{start_year}-01-01"
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# Step 2: Calculate Open-to-Close Range
def calculate_open_to_close_range(data):
    data['Open-Close Range'] = np.abs(data['Close'] - data['Open'])
    data['Open-Close Range Avg'] = data['Open-Close Range'].rolling(window=21).mean()
    return data

# Step 3: Calculate High-to-Low Range
def calculate_high_to_low_range(data):
    data['High-Low Range'] = data['High'] - data['Low']
    data['High-Low Range Avg'] = data['High-Low Range'].rolling(window=21).mean()
    return data

# Step 4: Calculate Wick Size
def calculate_wick_size(data):
    data['Upper Wick'] = data['High'] - data[['Open', 'Close']].max(axis=1)
    data['Lower Wick'] = data[['Open', 'Close']].min(axis=1) - data['Low']
    data['Upper Wick Avg'] = data['Upper Wick'].rolling(window=21).mean()
    data['Lower Wick Avg'] = data['Lower Wick'].rolling(window=21).mean()
    return data

# Step 5: Ensure Data Consistency
def ensure_data_consistency(data):
    numeric_columns = ['Open-Close Range', 'High-Low Range', 'Upper Wick', 'Lower Wick']
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors='coerce').fillna(0)
    return data

# Step 6: Visualize the Data
def visualize_data(data):
    data = ensure_data_consistency(data)

    def add_distribution_plot(ax, series, last_value):
        # Add the horizontal histogram and KDE plot
        divider = make_axes_locatable(ax)
        ax_hist = divider.append_axes("right", size="20%", pad=0.1)
        ax_hist.hist(series.dropna(), bins=30, orientation='horizontal', alpha=0.6)
        sns.kdeplot(series.dropna(), ax=ax_hist, vertical=True)
        ax_hist.axhline(last_value, color='r', linestyle='--')
        ax_hist.set_yticks([])

    last_open_close = data['Open-Close Range'].iloc[-1]
    last_high_low = data['High-Low Range'].iloc[-1]
    last_upper_wick = data['Upper Wick'].iloc[-1]
    last_lower_wick = data['Lower Wick'].iloc[-1]

    # First Window: Open-Close and High-Low Ranges
    fig1, axes1 = plt.subplots(2, 1, figsize=(14, 10))

    sns.lineplot(x=data.index, y=data['Open-Close Range'], ax=axes1[0], label='Open-Close Range')
    sns.lineplot(x=data.index, y=data['Open-Close Range Avg'], ax=axes1[0], label='Open-Close Range Avg')
    axes1[0].set_title('Daily Open-Close Range')
    axes1[0].legend(loc='upper left')
    add_distribution_plot(axes1[0], data['Open-Close Range'], last_open_close)

    sns.lineplot(x=data.index, y=data['High-Low Range'], ax=axes1[1], label='High-Low Range')
    sns.lineplot(x=data.index, y=data['High-Low Range Avg'], ax=axes1[1], label='High-Low Range Avg')
    axes1[1].set_title('Daily High-Low Range')
    axes1[1].legend(loc='upper left')
    add_distribution_plot(axes1[1], data['High-Low Range'], last_high_low)

    plt.tight_layout()
    plt.show()

    # Second Window: Upper and Lower Wick Sizes
    fig2, axes2 = plt.subplots(2, 1, figsize=(14, 10))

    sns.lineplot(x=data.index, y=data['Upper Wick'], ax=axes2[0], label='Upper Wick')
    sns.lineplot(x=data.index, y=data['Upper Wick Avg'], ax=axes2[0], label='Upper Wick Avg')
    axes2[0].set_title('Daily Upper Wick Sizes')
    axes2[0].legend(loc='upper left')
    add_distribution_plot(axes2[0], data['Upper Wick'], last_upper_wick)

    sns.lineplot(x=data.index, y=data['Lower Wick'], ax=axes2[1], label='Lower Wick')
    sns.lineplot(x=data.index, y=data['Lower Wick Avg'], ax=axes2[1], label='Lower Wick Avg')
    axes2[1].set_title('Daily Lower Wick Sizes')
    axes2[1].legend(loc='upper left')
    add_distribution_plot(axes2[1], data['Lower Wick'], last_lower_wick)

    plt.tight_layout()
    plt.show()

# Main Function
def main():
    ticker = input("Enter the stock symbol for analysis (e.g., AAPL, SPY): ").upper()  # Input for symbol
    start_year = input("Enter the start year for analysis (e.g., 2000): ")
    
    data = fetch_data(ticker, start_year)
    data = calculate_open_to_close_range(data)
    data = calculate_high_to_low_range(data)
    data = calculate_wick_size(data)
    
    visualize_data(data)

if __name__ == "__main__":
    main()
