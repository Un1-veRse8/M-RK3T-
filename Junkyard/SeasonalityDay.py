import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

def load_data():
    ticker = "^GSPC"  # S&P 500 ticker symbol
    end_date = datetime.now()
    start_date = datetime(end_date.year - 25, end_date.month, end_date.day)
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        print("Failed to download data:", e)
        return pd.DataFrame()

def prepare_data(df):
    df['Day of Week'] = df['Date'].dt.day_name()
    df['Daily Return'] = df['Adj Close'].pct_change()
    return df

def compute_statistics(df):
    return df.groupby('Day of Week')['Daily Return'].agg(['mean', 'min', 'max'])

def plot_statistics(stats):
    fig, ax = plt.subplots(3, 1, figsize=(10, 15))

    # Average Returns
    ax[0].bar(stats.index, stats['mean'], color='skyblue')
    ax[0].set_title('Average Returns by Day of Week')
    ax[0].set_ylabel('Average Return')

    # Minimum Returns
    ax[1].bar(stats.index, stats['min'], color='salmon')
    ax[1].set_title('Minimum Returns by Day of Week')
    ax[1].set_ylabel('Minimum Return')

    # Maximum Returns
    ax[2].bar(stats.index, stats['max'], color='lightgreen')
    ax[2].set_title('Maximum Returns by Day of Week')
    ax[2].set_ylabel('Maximum Return')

    for axis in ax:
        axis.set_xlabel('Day of the Week')
        axis.grid(True)

    plt.tight_layout()
    plt.show()

def spx_day_of_week_stats():
    df = load_data()
    if df.empty:
        print("Data loading is not properly implemented. Load your SPX data first.")
        return
    prepared_data = prepare_data(df)
    stats = compute_statistics(prepared_data)
    plot_statistics(stats)

# Example usage:
spx_day_of_week_stats()
