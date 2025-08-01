import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def fetch_monthly_returns(symbol, start_year):
    # Download historical data up to the most recent available date
    data = yf.download(symbol, start=f'{start_year - 1}-12-01', interval='1mo')
    data['Year'] = data.index.year
    data['Month'] = data.index.month

    # Calculate monthly returns
    data['Monthly Return'] = data['Adj Close'].pct_change() * 100

    # Pivot table to get a matrix of monthly returns
    monthly_returns = data.pivot_table(index='Year', columns='Month', values='Monthly Return')

    # Ensure all months are represented for each year
    all_months = pd.DataFrame(index=monthly_returns.index, columns=range(1, 13))
    monthly_returns = monthly_returns.combine_first(all_months)

    # Calculate additional statistics
    avg_returns = monthly_returns.mean()
    std_devs = monthly_returns.std()
    pos_percentages = (monthly_returns > 0).sum() / monthly_returns.count() * 100

    # Add the statistics as new rows
    monthly_returns.loc['Avg'] = avg_returns
    monthly_returns.loc['StDev'] = std_devs
    monthly_returns.loc['Pos%'] = pos_percentages

    return monthly_returns

def plot_seasonality_heatmap(monthly_returns):
    fig, ax = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [4, 1]})
    
    # Plot the heatmap for the main data
    sns.heatmap(
        monthly_returns.iloc[:-3], annot=True, fmt=".2f", cmap='RdYlGn', center=0,
        linewidths=0.5, linecolor='gray', ax=ax[0], cbar=False
    )
    ax[0].set_title('Seasonality Heatmap')
    ax[0].set_xlabel('Month')
    ax[0].set_ylabel('Year')
    
    # Plot the statistics below
    metrics = monthly_returns.iloc[-3:]
    sns.heatmap(
        metrics, annot=True, fmt=".2f", cmap='Greys', center=0, linewidths=0.5,
        linecolor='gray', ax=ax[1], cbar=False
    )
    ax[1].set_xlabel('Month')
    ax[1].set_ylabel('Metrics')
    
    # Adjust layout to make room for the second heatmap
    plt.tight_layout()
    plt.show()

def main():
    symbol = input("Enter the stock symbol (e.g., 'AAPL'): ").strip()
    start_year = int(input("Enter the starting year for analysis: "))
    
    monthly_returns = fetch_monthly_returns(symbol, start_year)
    plot_seasonality_heatmap(monthly_returns)

if __name__ == "__main__":
    main()
