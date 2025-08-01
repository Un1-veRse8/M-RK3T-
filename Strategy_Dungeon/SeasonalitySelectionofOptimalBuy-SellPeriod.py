import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product

def get_data(ticker):
    """Fetch historical data for a given ticker."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="max")
    return hist

def backtest_strategy(data, buy_month, sell_month):
    """Backtest a buy-in-buy_month and sell-in-sell_month strategy with a maximum holding period."""
    data['Returns'] = data['Close'].pct_change()
    data['Month'] = data.index.month
    data['Year'] = data.index.year

    signals = pd.DataFrame(index=data.index)
    signals['Position'] = 0

    # Buy in buy_month, sell in sell_month
    if buy_month < sell_month:
        signals.loc[(data['Month'] >= buy_month) & (data['Month'] < sell_month), 'Position'] = 1
    else:
        signals.loc[(data['Month'] >= buy_month) | (data['Month'] < sell_month), 'Position'] = 1

    # Ensure the holding period does not exceed 12 months
    signals['Position'] = signals['Position'].groupby((signals['Position'] != signals['Position'].shift()).cumsum()).cumcount() < 12

    # Forward fill the positions to hold the position until selling
    signals['Position'] = signals['Position'].ffill().fillna(0)

    # Calculate strategy returns
    signals['Strategy Returns'] = signals['Position'].shift(1) * data['Returns']

    cumulative_returns = (1 + signals['Strategy Returns']).cumprod()
    final_return = cumulative_returns.iloc[-1]

    return final_return, calculate_sharpe_ratio(signals['Strategy Returns'])

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    """Calculate the annualized Sharpe ratio of the strategy."""
    excess_returns = returns - risk_free_rate / 252
    sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    return sharpe_ratio

def find_best_seasonality(ticker):
    """Find the best buy and sell months for a given ticker."""
    data = get_data(ticker)
    
    results = []
    for buy_month, sell_month in product(range(1, 13), repeat=2):
        if buy_month != sell_month:
            final_return, sharpe_ratio = backtest_strategy(data, buy_month, sell_month)
            results.append((buy_month, sell_month, final_return, sharpe_ratio))
    
    results_df = pd.DataFrame(results, columns=['Buy Month', 'Sell Month', 'Final Return', 'Sharpe Ratio'])
    
    return results_df

def find_best_periods(ticker, holding_period):
    """Find the best buy and sell months for a given ticker for a specific holding period."""
    data = get_data(ticker)
    
    results = []
    for buy_month in range(1, 13):
        sell_month = (buy_month + holding_period) % 12
        if sell_month == 0:
            sell_month = 12
        
        final_return, sharpe_ratio = backtest_strategy(data, buy_month, sell_month)
        results.append((buy_month, sell_month, final_return, sharpe_ratio))
    
    results_df = pd.DataFrame(results, columns=['Buy Month', 'Sell Month', 'Final Return', 'Sharpe Ratio'])
    
    # Find the best result based on Final Return
    best_return_row = results_df.loc[results_df['Final Return'].idxmax()]
    best_return = {
        'Buy Month': best_return_row['Buy Month'],
        'Sell Month': best_return_row['Sell Month'],
        'Final Return': best_return_row['Final Return']
    }
    
    # Find the best result based on Sharpe Ratio
    best_sharpe_row = results_df.loc[results_df['Sharpe Ratio'].idxmax()]
    best_sharpe = {
        'Buy Month': best_sharpe_row['Buy Month'],
        'Sell Month': best_sharpe_row['Sell Month'],
        'Sharpe Ratio': best_sharpe_row['Sharpe Ratio']
    }
    
    return best_return, best_sharpe

def plot_heatmap(data, title):
    """Plot a heatmap for the given data."""
    plt.figure(figsize=(10, 8))
    sns.heatmap(data, annot=True, cmap="YlGnBu", fmt=".2f")
    plt.title(title)
    plt.show()

def main():
    ticker = input("Enter the ticker symbol: ").upper()
    
    results_df = find_best_seasonality(ticker)
    
    pivot_final_return = results_df.pivot(index='Buy Month', columns='Sell Month', values='Final Return')
    pivot_sharpe_ratio = results_df.pivot(index='Buy Month', columns='Sell Month', values='Sharpe Ratio')
    
    plot_heatmap(pivot_final_return, 'Final Return Heatmap')
    plot_heatmap(pivot_sharpe_ratio, 'Sharpe Ratio Heatmap')

    # Find the best buy and sell month based on Final Return
    max_return = pivot_final_return.max().max()
    best_return_pair = pivot_final_return.stack().idxmax()
    
    # Find the best buy and sell month based on Sharpe Ratio
    max_sharpe = pivot_sharpe_ratio.max().max()
    best_sharpe_pair = pivot_sharpe_ratio.stack().idxmax()
    
    print(f"Best Buy-Sell Month Pair based on Final Return: Buy Month {best_return_pair[0]}, Sell Month {best_return_pair[1]} with a Final Return of {max_return:.2f}")
    print(f"Best Buy-Sell Month Pair based on Sharpe Ratio: Buy Month {best_sharpe_pair[0]}, Sell Month {best_sharpe_pair[1]} with a Sharpe Ratio of {max_sharpe:.2f}")
    
    periods = [2, 3, 4, 6]
    
    for period in periods:
        best_return, best_sharpe = find_best_periods(ticker, period)
        print(f"Best {period}-Month Period based on Final Return: Buy Month {best_return['Buy Month']}, Sell Month {best_return['Sell Month']} with a Final Return of {best_return['Final Return']:.2f}")
        print(f"Best {period}-Month Period based on Sharpe Ratio: Buy Month {best_sharpe['Buy Month']}, Sell Month {best_sharpe['Sell Month']} with a Sharpe Ratio of {best_sharpe['Sharpe Ratio']:.2f}")
        print("")

if __name__ == "__main__":
    main()
