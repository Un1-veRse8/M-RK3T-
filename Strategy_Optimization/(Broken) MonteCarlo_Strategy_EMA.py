import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

def calculate_ema(prices, span=20):
    return prices.ewm(span=span, adjust=False).mean()

def ema_strategy(prices, fast=12, slow=26):
    ema_fast = calculate_ema(prices, span=fast)
    ema_slow = calculate_ema(prices, span=slow)
    buy_signals = ema_fast > ema_slow
    sell_signals = ema_fast < ema_slow
    return buy_signals, sell_signals

def run_simulation(data, fast, slow):
    # Monte Carlo simulation
    sims = 100  # Number of simulations
    steps = 252  # Number of trading days in one year
    portfolio_values = pd.DataFrame()

    np.random.seed(0)
    for sim in range(sims):
        prices = [data['Adj Close'].iloc[-1]]
        for _ in range(1, steps):
            prices.append(prices[-1] * (1 + np.random.normal(data['Return'].mean(), data['Return'].std())))
        prices = pd.Series(prices)
        
        buy_signals, sell_signals = ema_strategy(prices, fast=fast, slow=slow)
        
        # Trading simulation
        cash = 10000
        holdings = 0
        portfolio = [cash]
        for i in range(1, len(prices)):
            if buy_signals[i] and cash > 0:
                holdings = cash / prices[i]
                cash = 0
            elif sell_signals[i] and holdings > 0:
                cash = holdings * prices[i]
                holdings = 0
            portfolio.append(cash + holdings * prices[i])

        portfolio_values[sim] = portfolio

    return portfolio_values

def evaluate_strategy(portfolio_values):
    # Calculate performance metrics
    daily_returns = portfolio_values.pct_change().fillna(0)
    mean_daily_returns = daily_returns.mean(axis=1)
    risk_free_rate = yf.download("^IRX", start="2000-01-01", end="2024-05-10")['Adj Close'].iloc[-1] / 100 / 252  # 3-month T-bill rate

    # Sharpe Ratio
    excess_daily_returns = mean_daily_returns - risk_free_rate
    sharpe_ratio = np.sqrt(252) * excess_daily_returns.mean() / daily_returns.std().mean()

    # Sortino Ratio
    negative_returns = daily_returns[daily_returns < 0]
    sortino_ratio = np.sqrt(252) * excess_daily_returns.mean() / negative_returns.std(ddof=1).mean()

    # Total Return
    total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1).mean() * 100

    return sharpe_ratio, sortino_ratio, total_return

def plot_results(portfolio_values, sharpe_ratio, sortino_ratio, total_return):
    plt.figure(figsize=(14, 7))
    for column in portfolio_values:
        plt.plot(portfolio_values.index, portfolio_values[column], lw=1, alpha=0.1)  # Plot each simulation path with low opacity

    mean_portfolio = portfolio_values.mean(axis=1)
    plt.plot(mean_portfolio, label='Mean Portfolio Value', color='blue', lw=2)

    plt.title('Monte Carlo Simulation with EMA Strategy Across Multiple Paths')
    plt.xlabel('Days')
    plt.ylabel('Portfolio Value')
    plt.legend(title=f'Sharpe Ratio: {sharpe_ratio:.2f}, Sortino Ratio: {sortino_ratio:.2f}, Total Return: {total_return:.2f}%')
    plt.show()

# Fetch data
data = yf.download('SPY', start="2000-01-01", end="2024-05-10")
data['Return'] = data['Adj Close'].pct_change().fillna(0)

# Split data into training and testing periods
train_length = 10 * 252  # 10 years for training
test_length = 2 * 252  # 2 years for testing
train_data = data.iloc[:train_length]
test_data = data.iloc[train_length:train_length + test_length]

# Parameters for the EMA strategy
fast_ema_values = range(10, 50, 5)  # (start, stop, step)
slow_ema_values = range(20, 100, 10)  # (start, stop, step)

# Grid search for best parameters
best_sharpe_ratio = -np.inf
best_fast, best_slow = None, None
for fast in fast_ema_values:
    for slow in slow_ema_values:
        if slow > fast:  # Ensure slow EMA period is longer than fast EMA period
            portfolio_values = run_simulation(train_data, fast, slow)
            sharpe_ratio, _, _ = evaluate_strategy(portfolio_values)
            if sharpe_ratio > best_sharpe_ratio:
                best_sharpe_ratio = sharpe_ratio
                best_fast, best_slow = fast, slow

print(f'Best parameters found: Fast EMA = {best_fast}, Slow EMA = {best_slow}, Sharpe Ratio = {best_sharpe_ratio}')

# Run final simulation with best parameters on test data
best_portfolio_values = run_simulation(test_data, best_fast, best_slow)

# Evaluate the strategy with best parameters on test data
best_sharpe_ratio, best_sortino_ratio, best_total_return = evaluate_strategy(best_portfolio_values)

# Plot the results with best parameters
plot_results(best_portfolio_values, best_sharpe_ratio, best_sortino_ratio, best_total_return)
