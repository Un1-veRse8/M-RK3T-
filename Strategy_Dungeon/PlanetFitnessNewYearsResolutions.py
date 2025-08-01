import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_data(ticker):
    """Fetch historical data for a given ticker."""
    return yf.download(ticker, start="2010-01-01", end="2024-01-01")

def backtest_strategy(data):
    """Backtest the buy-in-November and sell-in-January strategy."""
    data['Returns'] = data['Adj Close'].pct_change()
    data['Month'] = data.index.month
    data['Year'] = data.index.year
    
    signals = pd.DataFrame(index=data.index)
    signals['Position'] = 0
    
    # Buy in November, sell in January
    signals.loc[(data['Month'] == 11), 'Position'] = 1
    signals.loc[(data['Month'] == 10), 'Position'] = 0
    
    # Forward fill the positions
    signals['Position'] = signals['Position'].ffill().fillna(0)
    
    # Calculate strategy returns
    signals['Strategy Returns'] = signals['Position'].shift(1) * data['Returns']
    
    return signals, data

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    """Calculate the annualized Sharpe ratio of the strategy."""
    excess_returns = returns - risk_free_rate / 252
    sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    return sharpe_ratio

def plot_results(data, signals, initial_investment=10000):
    """Plot the performance of the strategy and show returns on initial investment."""
    cumulative_returns = (1 + signals['Strategy Returns']).cumprod()
    final_value = initial_investment * cumulative_returns[-1]
    
    cumulative_returns.plot(figsize=(10, 5))
    plt.title('Strategy Performance, Buy Planet Fitness in Nov Sell in Jan')
    plt.ylabel('Cumulative Returns')
    plt.show()
    
    print(f'Final value of ${initial_investment} investment: ${final_value:.2f}')

# Fetch data
ticker = 'PLNT'
data = get_data(ticker)

# Backtest strategy
signals, data = backtest_strategy(data)

# Calculate Sharpe ratio
sharpe_ratio = calculate_sharpe_ratio(signals['Strategy Returns'])
print(f'Sharpe Ratio: {sharpe_ratio}')

# Plot results and show final investment value
plot_results(data, signals, initial_investment=10000)
