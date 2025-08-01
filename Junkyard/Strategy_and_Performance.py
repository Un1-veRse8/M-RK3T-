import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import ParameterGrid

# Fetch historical data
data = yf.download('^GSPC', start='1980-01-01', end=None)

# Calculate MACD
def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
    slow_ema = prices.ewm(span=slow_period, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    return macd_line, signal_line

# Evaluate MACD strategy
def evaluate_strategy(prices, macd_line, signal_line, initial_cash=10000):
    buy_signals = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
    sell_signals = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))
    
    cash = initial_cash
    holdings = 0
    portfolio = [cash]
    for i in range(1, len(prices)):
        if buy_signals.iloc[i] and cash > 0:
            holdings = cash / prices.iloc[i]
            cash = 0
        elif sell_signals.iloc[i] and holdings > 0:
            cash = holdings * prices.iloc[i]
            holdings = 0
        portfolio.append(cash + holdings * prices.iloc[i] if holdings > 0 else cash)
    return portfolio[-1], portfolio

# Define parameter grid with expanded ranges
param_grid = {
    'fast_period': [6, 12, 18],
    'slow_period': [13, 26, 39],
    'signal_period': [4, 9, 14]
}

# Initialize results list
results = []

# Perform grid search
for params in ParameterGrid(param_grid):
    fast_period = params['fast_period']
    slow_period = params['slow_period']
    signal_period = params['signal_period']
    
    # Calculate MACD
    macd_line, signal_line = calculate_macd(data['Close'], fast_period, slow_period, signal_period)
    
    # Evaluate strategy
    final_value, portfolio = evaluate_strategy(data['Close'], macd_line, signal_line)
    results.append((fast_period, slow_period, signal_period, final_value, portfolio))

# Find the best parameters
best_params = max(results, key=lambda x: x[3])

# Print the results
print("Original periods tested:")
for key, value in param_grid.items():
    print(f"{key} periods: {value}")

print(f"\nBest Parameters: Fast Period = {best_params[0]}, Slow Period = {best_params[1]}, Signal Period = {best_params[2]}")
print(f"Best Cumulative Strategy Return: {best_params[3]}")
print("\nThe data has been automatically updated with the best-found parameters.")

# Extract best portfolio
best_portfolio = best_params[4]

# Ensure cumulative returns are calculated properly
data['MACD_Line'], data['Signal_Line'] = calculate_macd(data['Close'], best_params[0], best_params[1], best_params[2])
buy_signals = (data['MACD_Line'] > data['Signal_Line']) & (data['MACD_Line'].shift(1) <= data['Signal_Line'].shift(1))
sell_signals = (data['MACD_Line'] < data['Signal_Line']) & (data['MACD_Line'].shift(1) >= data['Signal_Line'].shift(1))
data['Buy_Signal'] = buy_signals
data['Sell_Signal'] = sell_signals
data['Position'] = 0
data.loc[buy_signals, 'Position'] = 1
data.loc[sell_signals, 'Position'] = -1
data['Market_Return'] = data['Close'].pct_change()
data['Strategy_Return'] = data['Market_Return'] * data['Position'].shift(1)
data['Cumulative_Market_Return'] = (1 + data['Market_Return']).cumprod()
data['Cumulative_Strategy_Return'] = (1 + data['Strategy_Return']).cumprod()

# Ensure portfolio values align with cumulative strategy returns
data['Portfolio_Value'] = [10000] + best_portfolio[:-1]
data['Cumulative_Strategy_Return'] = data['Portfolio_Value'] / 10000

# Plot the results
fig, axs = plt.subplots(1, 2, figsize=(14, 7))

axs[0].plot(data['Cumulative_Market_Return'], label='Market Return')
axs[0].set_title('Market Return')
axs[0].legend()

axs[1].plot(data['Cumulative_Strategy_Return'], label='Strategy Return')
axs[1].set_title('Strategy Return')
axs[1].legend()

plt.tight_layout()
plt.show()
