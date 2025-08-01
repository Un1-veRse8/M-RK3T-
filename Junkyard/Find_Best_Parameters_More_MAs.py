import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime

# Define functions for different types of moving averages
def calculate_ema(prices, span=20):
    """Calculate Exponential Moving Average."""
    return prices.ewm(span=span, adjust=False).mean()

def calculate_sma(prices, span=20):
    """Calculate Simple Moving Average."""
    return prices.rolling(window=span).mean()

def calculate_wma(prices, span=20):
    """Calculate Weighted Moving Average."""
    weights = np.arange(1, span + 1)
    return prices.rolling(window=span).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def calculate_hma(prices, span=20):
    """Calculate Hull Moving Average."""
    half_length = int(span / 2)
    sqrt_length = int(np.sqrt(span))
    wma_half_length = calculate_wma(prices, half_length)
    wma_full_length = calculate_wma(prices, span)
    raw_hma = 2 * wma_half_length - wma_full_length
    return calculate_wma(raw_hma, sqrt_length)

def calculate_tma(prices, span=20):
    """Calculate Triangular Moving Average."""
    sma_1 = calculate_sma(prices, span)
    return calculate_sma(sma_1, span)

def calculate_kama(prices, span=20, fast=2, slow=30):
    """Calculate Kaufman's Adaptive Moving Average."""
    ER = prices.diff().abs().rolling(window=span).sum() / prices.diff(span).abs()
    SC = ((ER * (2 / (fast + 1) - 2 / (slow + 1)) + 2 / (slow + 1)) ** 2)
    KAMA = prices.copy()
    for i in range(1, len(prices)):
        KAMA.iloc[i] = KAMA.iloc[i - 1] + SC.iloc[i] * (prices.iloc[i] - KAMA.iloc[i - 1])
    return KAMA

def calculate_vwap(prices, volume, span=20):
    """Calculate Volume-Weighted Average Price."""
    return (prices * volume).rolling(window=span).sum() / volume.rolling(window=span).sum()

def calculate_dema(prices, span=20):
    """Calculate Double Exponential Moving Average."""
    ema = calculate_ema(prices, span)
    dema = 2 * ema - calculate_ema(ema, span)
    return dema

def calculate_tema(prices, span=20):
    """Calculate Triple Exponential Moving Average."""
    ema = calculate_ema(prices, span)
    dema = 2 * ema - calculate_ema(ema, span)
    tema = 3 * dema - calculate_ema(dema, span)
    return tema

def calculate_rochl(prices, highs, lows, recursive=False):
    """Calculate Ratio OCHL Averager."""
    d = pd.Series(np.zeros(len(prices)), index=prices.index)
    a = prices.copy()
    for i in range(1, len(prices)):
        if recursive:
            a.iloc[i] = d.iloc[i - 1]
        else:
            a.iloc[i] = prices.iloc[0]  # Assuming 'open' is the first price
        b = abs(prices.iloc[i] - a.iloc[i]) / (highs.iloc[i] - lows.iloc[i])
        c = min(1, b)
        d.iloc[i] = c * prices.iloc[i] + (1 - c) * d.iloc[i - 1]
    return d

# General MA strategy function that can use various types of MAs
def ma_strategy(prices, highs, lows, fast, slow, ma_type='ema'):
    if ma_type == 'ema':
        fast_ma = calculate_ema(prices, span=fast)
        slow_ma = calculate_ema(prices, span=slow)
    elif ma_type == 'sma':
        fast_ma = calculate_sma(prices, span=fast)
        slow_ma = calculate_sma(prices, span=slow)
    elif ma_type == 'wma':
        fast_ma = calculate_wma(prices, span=fast)
        slow_ma = calculate_wma(prices, span=slow)
    elif ma_type == 'hma':
        fast_ma = calculate_hma(prices, span=fast)
        slow_ma = calculate_hma(prices, span=slow)
    elif ma_type == 'tma':
        fast_ma = calculate_tma(prices, span=fast)
        slow_ma = calculate_tma(prices, span=slow)
    elif ma_type == 'kama':
        fast_ma = calculate_kama(prices, span=fast)
        slow_ma = calculate_kama(prices, span=slow)
    elif ma_type == 'vwap':
        volume = data['Volume']
        fast_ma = calculate_vwap(prices, volume, span=fast)
        slow_ma = calculate_vwap(prices, volume, span=slow)
    elif ma_type == 'dema':
        fast_ma = calculate_dema(prices, span=fast)
        slow_ma = calculate_dema(prices, span=slow)
    elif ma_type == 'tema':
        fast_ma = calculate_tema(prices, span=fast)
        slow_ma = calculate_tema(prices, span=slow)
    elif ma_type == 'rochl':
        fast_ma = calculate_rochl(prices, highs, lows, recursive=False)
        slow_ma = calculate_rochl(prices, highs, lows, recursive=False)
    else:
        raise ValueError("MA type not supported.")
    
    buy_signals = fast_ma > slow_ma
    sell_signals = fast_ma < slow_ma
    return buy_signals, sell_signals

# Function to evaluate the strategy
def evaluate_strategy(prices, highs, lows, fast, slow, ma_type='ema', initial_cash=10000):
    buy_signals, sell_signals = ma_strategy(prices, highs, lows, fast, slow, ma_type)
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
    return portfolio[-1]

# Prompt user for inputs
ticker = input("Enter the ticker symbol you'd like to test (e.g., 'SPY'): ").strip()
start_year = input("Enter the start year for historical data (e.g., '2000'): ").strip()
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = f"{start_year}-01-01"

# Download historical data
data = yf.download(ticker, start=start_date, end=end_date)
prices = data['Adj Close']
highs = data['High']
lows = data['Low']

# Define the list of MA types
ma_types = ['ema', 'sma', 'wma', 'hma', 'tma', 'kama', 'vwap', 'dema', 'tema', 'rochl']

# Prompt user for the MA type
print("Available moving average types:")
for i, ma_type in enumerate(ma_types, 1):
    print(f"{i}. {ma_type.upper()}")
try:
    selected_ma_type_index = int(input("Enter the number of the MA type you'd like to test: ").strip()) - 1
    selected_ma_type = ma_types[selected_ma_type_index]
except (ValueError, IndexError):
    print("Invalid input. Please enter a valid number corresponding to the MA type.")
    exit()

# Prompt user for the range of fast and slow MA parameters
fast_range_start = int(input("Enter the start of the fast MA range (e.g., 5): ").strip())
fast_range_end = int(input("Enter the end of the fast MA range (e.g., 20): ").strip())
slow_range_start = int(input("Enter the start of the slow MA range (e.g., 20): ").strip())
slow_range_end = int(input("Enter the end of the slow MA range (e.g., 50): ").strip())

# Define the range of MA parameters to test
fast_range = range(fast_range_start, fast_range_end + 1)
slow_range = range(slow_range_start, slow_range_end + 1)
results = []

# Perform grid search to find the best parameters
for fast in fast_range:
    for slow in slow_range:
        if slow > fast:
            final_value = evaluate_strategy(prices, highs, lows, fast, slow, ma_type=selected_ma_type)
            results.append({"MA Type": selected_ma_type, "Fast": fast, "Slow": slow, "Final Value": final_value})

# Convert the results into a DataFrame
results_df = pd.DataFrame(results)

# Find the best parameters
best_parameters = results_df.loc[results_df['Final Value'].idxmax()]

print("Best Parameters:")
print(best_parameters)

# Plotting
fig, ax = plt.subplots()
sc = ax.scatter(results_df['Fast'], results_df['Slow'], c=results_df['Final Value'], label=f'{selected_ma_type.upper()} MA', cmap='viridis', alpha=0.6)
plt.colorbar(sc, ax=ax, label='Final Portfolio Value')
ax.set_xlabel('Fast MA')
ax.set_ylabel('Slow MA')
ax.set_title('Optimization Results of MA Parameters')
ax.legend(title='MA Type')
plt.show()
