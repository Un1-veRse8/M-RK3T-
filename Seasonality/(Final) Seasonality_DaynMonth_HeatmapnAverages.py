import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def fetch_daily_returns(symbol, start_year):
    # Download historical data up to the most recent available date
    end_date = datetime.now()
    data = yf.download(symbol, start=f'{start_year}-01-01', end=end_date)
    data['Year'] = data.index.year
    data['Month'] = data.index.month
    data['Day'] = data.index.day

    # Calculate daily returns
    data['Daily Return'] = data['Adj Close'].pct_change() * 100

    # Filter data for the specified range
    data = data[data['Year'] >= start_year]

    # Pivot table to get a matrix of daily returns
    daily_returns = data.pivot_table(index='Month', columns='Day', values='Daily Return')

    # Calculate the average returns
    avg_returns = daily_returns.mean()

    return daily_returns, avg_returns

def plot_seasonality_heatmap(daily_returns, avg_returns, symbol, start_year):
    fig, ax = plt.subplots(2, 1, figsize=(18, 12), gridspec_kw={'height_ratios': [4, 1]})
    
    # Plot the heatmap for the main data
    sns.heatmap(
        daily_returns, annot=True, fmt=".2f", cmap='viridis', center=0,
        linewidths=0.5, linecolor='gray', ax=ax[0], cbar=False,
        annot_kws={'color': 'white'}
    )
    ax[0].set_title(f'Seasonality Heatmap for {symbol} from {start_year} to {datetime.now().year}')
    ax[0].set_xlabel('Day of Month')
    ax[0].set_ylabel('Month')

    # Highlight the current month and day
    current_month = datetime.now().month
    current_day = datetime.now().day
    ax[0].add_patch(plt.Rectangle((current_day-1, current_month-1), 1, 1, fill=False, edgecolor='black', lw=2))
    
    # Plot the average returns below
    avg_df = pd.DataFrame([avg_returns], index=['Avg'])
    sns.heatmap(
        avg_df, annot=True, fmt=".2f", cmap='viridis', center=0, linewidths=0.5,
        linecolor='gray', ax=ax[1], cbar=False, annot_kws={'color': 'white'}
    )
    ax[1].set_xlabel('Day of Month')
    ax[1].set_ylabel('Metrics')
    
    # Highlight the current day in the averages
    ax[1].add_patch(plt.Rectangle((current_day-1, 0), 1, 1, fill=False, edgecolor='black', lw=2))
    
    # Adjust layout to make room for the second heatmap
    plt.tight_layout()

    # Add text annotation for website or Twitter handle
    fig.text(0.99, 0.01, 'Twitter Handle: @o5341V', horizontalalignment='right')

    # Set window size and position
    manager = plt.get_current_fig_manager()
    manager.window.wm_geometry("+50+50")  # Adjust position as needed
    manager.window.state('zoomed')  # Maximize the window

    plt.show()

def main():
    symbol = input("Enter the stock symbol (e.g., 'AAPL'): ").strip()
    start_year = int(input("Enter the starting year for analysis: "))
    
    daily_returns, avg_returns = fetch_daily_returns(symbol, start_year)
    plot_seasonality_heatmap(daily_returns, avg_returns, symbol, start_year)

if __name__ == "__main__":
    main()
