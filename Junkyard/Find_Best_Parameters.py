import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

def calculate_ema(prices, span=20):
    return prices.ewm(span=span, adjust=False).mean()

def ema_strategy(prices, fast, slow):
    ema_fast = calculate_ema(prices, span=fast)
    ema_slow = calculate_ema(prices, span=slow)
    buy_signals = ema_fast > ema_slow
    sell_signals = ema_fast < ema_slow
    return buy_signals, sell_signals

def evaluate_strategy(prices, fast, slow, initial_cash=10000):
    buy_signals, sell_signals = ema_strategy(prices, fast, slow)
    cash = initial_cash
    holdings = 0
    portfolio = [cash]
    for i in range(1, len(prices)):
        if buy_signals.iloc[i] and cash > 0:  # Use .iloc for positional indexing
            holdings = cash / prices.iloc[i]  # Use .iloc for positional indexing
            cash = 0
        elif sell_signals.iloc[i] and holdings > 0:  # Use .iloc for positional indexing
            cash = holdings * prices.iloc[i]  # Use .iloc for positional indexing
            holdings = 0
        portfolio.append(cash + holdings * prices.iloc[i] if holdings > 0 else cash)
    return portfolio[-1]

data = yf.download('SPY', start="2000-01-01", end="2024-05-10")
prices = data['Adj Close']

fast_range = range(5, 52)
slow_range = range(5, 52)
results = []

for fast in fast_range:
    for slow in slow_range:
        if slow > fast:
            final_value = evaluate_strategy(prices, fast, slow)
            results.append({"Fast": fast, "Slow": slow, "Final Value": final_value})

# Convert list of dictionaries to DataFrame
results_df = pd.DataFrame(results)

# Find the best parameters
best_parameters = results_df.loc[results_df['Final Value'].idxmax()]

print("Best Parameters:")
print(best_parameters)

# Plotting
plt.scatter(results_df['Fast'], results_df['Slow'], c=results_df['Final Value'], cmap='viridis')
plt.colorbar(label='Final Portfolio Value')
plt.xlabel('Fast EMA')
plt.ylabel('Slow EMA')
plt.title('Optimization Results of EMA Parameters')
plt.show()
