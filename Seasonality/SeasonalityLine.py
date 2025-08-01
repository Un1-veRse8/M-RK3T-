import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

def load_data():
    ticker = "^GSPC"  # S&P 500 ticker symbol
    end_date = datetime.now()
    start_date = datetime(end_date.year - 20, end_date.month, end_date.day)
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        print("Failed to download data:", e)
        return pd.DataFrame()

def prepare_data(df, start_year):
    df = df[df['Date'].dt.year >= start_year]
    df['Month'] = df['Date'].dt.month
    df['Daily Return'] = df['Adj Close'].pct_change()
    return df

def plot_monthly_averages(df):
    # Group by month and calculate average, min, and max of daily returns
    monthly_stats = df.groupby('Month')['Daily Return'].agg(['mean', 'min', 'max'])
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Bar plot for the average returns
    color = 'tab:blue'
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Average Return', color=color)
    ax1.bar(monthly_stats.index, monthly_stats['mean'], color=color, alpha=0.75, label='Monthly Average')
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Line plots for min and max on secondary axis
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Min/Max Return', color=color)
    ax2.plot(monthly_stats.index, monthly_stats['min'], color='red', linestyle='--', label='Monthly Min')
    ax2.plot(monthly_stats.index, monthly_stats['max'], color='green', linestyle='--', label='Monthly Max')
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    plt.title('Monthly Return Statistics for S&P 500')
    plt.xticks(ticks=range(1, 13), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.show()

def spx_monthly_averages(years_of_data):
    df = load_data()
    if df.empty:
        print("Data loading is not properly implemented. Load your SPX data first.")
        return
    start_year = datetime.now().year - years_of_data
    prepared_data = prepare_data(df, start_year)
    plot_monthly_averages(prepared_data)

# Example usage:
spx_monthly_averages(25)  # Adjust the number of years as needed
