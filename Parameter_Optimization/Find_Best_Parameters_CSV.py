import numpy as np
import pandas as pd
import yfinance as yf

def calculate_ema(prices, span):
    """Calculate the Exponential Moving Average over a specified span."""
    return prices.ewm(span=span, adjust=False).mean()

def ema_strategy(prices, fast, slow):
    """Generate buy and sell signals based on EMA crossovers."""
    ema_fast = calculate_ema(prices, span=fast)
    ema_slow = calculate_ema(prices, span=slow)
    buy_signals = ema_fast > ema_slow
    sell_signals = ema_fast < ema_slow
    return buy_signals, sell_signals

def evaluate_strategy(prices, fast, slow, initial_cash=10000):
    """Evaluate EMA strategy by simulating trades and calculating final portfolio value."""
    buy_signals, sell_signals = ema_strategy(prices, fast, slow)
    cash = initial_cash
    holdings = 0
    for i in range(1, len(prices)):
        if buy_signals.iloc[i] and cash > 0:
            holdings = cash / prices.iloc[i]
            cash = 0
        elif sell_signals.iloc[i] and holdings > 0:
            cash = holdings * prices.iloc[i]
            holdings = 0
    final_portfolio_value = cash + holdings * prices.iloc[-1] if holdings > 0 else cash
    return final_portfolio_value

# Download historical stock data
symbol = 'SPY'
data = yf.download(symbol, start="2010-01-01", end="2024-05-10")
prices = data['Adj Close']

# Define the range of EMA parameters to test
fast_range = range(5, 52)
slow_range = range(5, 52)

# Store the results
results = []

# Perform grid search to find the best parameters
for fast in fast_range:
    for slow in slow_range:
        if slow > fast:  # Ensure the slow EMA is greater than the fast EMA
            final_value = evaluate_strategy(prices, fast, slow)
            results.append({"Fast": fast, "Slow": slow, "Final Value": final_value})

# Convert the results into a DataFrame
results_df = pd.DataFrame(results)

# Save the results to a CSV file
results_df.to_csv('ema_optimization_results.csv', index=False)

# Print completion message
print("Optimization completed and results saved to 'ema_optimization_results.csv'.")
