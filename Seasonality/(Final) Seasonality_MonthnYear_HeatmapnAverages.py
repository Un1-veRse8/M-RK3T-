import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def fetch_monthly_returns(symbol, start_year):
    # Download historical data up to the most recent available date
    data = yf.download(symbol, start=f'{start_year - 1}-12-01', interval='1mo') #^GSPC ^VIX
    data['Year'] = data.index.year
    data['Month'] = data.index.month

    # Calculate monthly returns
    data['Monthly Return'] = data['Adj Close'].pct_change() * 100

    # Pivot table to get a matrix of monthly returns
    monthly_returns = data.pivot_table(index='Year', columns='Month', values='Monthly Return')

    # Ensure all months are represented for each year
    all_months = pd.DataFrame(index=monthly_returns.index, columns=range(1, 13))
    monthly_returns = monthly_returns.combine_first(all_months)

    # Calculate average returns
    avg_returns = monthly_returns.mean()

    # Add the average returns as a new row
    monthly_returns.loc['Avg'] = avg_returns

    return monthly_returns

def plot_seasonality_heatmap(monthly_returns, symbol, start_year):
    end_year = monthly_returns.index[-2]  # The last year in the data
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    fig, ax = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [4, 1]})
    
    # Plot the heatmap for the main data
    sns.heatmap(
        monthly_returns.iloc[:-1], annot=True, fmt=".2f", cmap='viridis', center=0, # https://matplotlib.org/stable/users/explain/colors/colormaps.html gist_gray
        linewidths=0.5, linecolor='white', ax=ax[0], cbar=False
    )
    ax[0].set_title(f'Seasonality Heatmap for {symbol.upper()} from {start_year} to {end_year}')
    ax[0].set_xlabel('Month')
    ax[0].set_ylabel('Year')

    # Make the borders of the current month and year cells thicker and set text color to black
    for text in ax[0].texts:
        if text.get_text() != '':
            x = int(text.get_position()[0]) + 1
            y = int(text.get_position()[1]) + 1
            text.set_color('black')
            if x == current_month and y == (current_year - start_year + 1):
                ax[0].add_patch(plt.Rectangle((text.get_position()[0] - 0.5, text.get_position()[1] - 0.5), 1, 1,
                                              fill=False, edgecolor='black', linewidth=2))
            else:
                text.set_color('white')

    # Plot the average returns below
    avg = monthly_returns.iloc[-1:]
    sns.heatmap(
        avg, annot=True, fmt=".2f", cmap='viridis', center=0, linewidths=0.5, 
        linecolor='white', ax=ax[1], cbar=False, yticklabels=['Avg']
    )
    ax[1].set_xlabel('Month')
    ax[1].set_ylabel('Metrics')
    ax[1].set_xticklabels(range(1, 13))

    # Make the borders of the current month cell in the average returns heatmap thicker and set text color to black
    for text in ax[1].texts:
        if text.get_text() != '':
            x = int(text.get_position()[0]) + 1
            if x == current_month:
                text.set_color('black')
                ax[1].add_patch(plt.Rectangle((text.get_position()[0] - 0.5, text.get_position()[1] - 0.5), 1, 1,
                                              fill=False, edgecolor='black', linewidth=2))
            else:
                text.set_color('white')
    
    # Adjust layout to make room for the second heatmap
    plt.tight_layout()

    # Add text annotation for website or Twitter handle
    fig.text(0.99, 0.01, 'Twitter Handle: @o5341V', horizontalalignment='right')

    # Set the window size and position
    manager = plt.get_current_fig_manager()
    manager.window.wm_geometry("+50+50")
    manager.window.state('zoomed')  # Maximize the window

    plt.show()

def main():
    symbol = input("Enter the stock symbol (e.g., '^GSPC, AAPL, ETC'): ").strip()
    start_year = int(input("Enter the starting year for analysis: "))
    
    monthly_returns = fetch_monthly_returns(symbol, start_year)
    plot_seasonality_heatmap(monthly_returns, symbol, start_year)

if __name__ == "__main__":
    main()