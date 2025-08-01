import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime

# Define functions for different oscillators
def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index (RSI)."""
    delta = prices.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_stochastic(prices, period=14):
    """Calculate Stochastic Oscillator."""
    low_min = prices.rolling(window=period).min()
    high_max = prices.rolling(window=period).max()
    return 100 * ((prices - low_min) / (high_max - low_min))

def calculate_cci(prices, period=20):
    """Calculate Commodity Channel Index (CCI)."""
    tp = (prices + prices + prices) / 3  # Typical price
    tp_sma = tp.rolling(window=period).mean()
    mean_deviation = (tp - tp_sma).abs().rolling(window=period).mean()
    return (tp - tp_sma) / (0.015 * mean_deviation)

def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """Calculate Moving Average Convergence Divergence (MACD)."""
    fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
    slow_ema = prices.ewm(span=slow_period, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    return macd_line, signal_line

def calculate_williams_r(prices, period=14):
    """Calculate Williams %R."""
    low_min = prices.rolling(window=period).min()
    high_max = prices.rolling(window=period).max()
    return -100 * ((high_max - prices) / (high_max - low_min))

# General strategy function using various oscillators
def oscillator_strategy(prices, highs, lows, period, osc_type='rsi'):
    if osc_type == 'rsi':
        oscillator = calculate_rsi(prices, period=period)
        buy_signals = oscillator < 30
        sell_signals = oscillator > 70
    elif osc_type == 'stochastic':
        oscillator = calculate_stochastic(prices, period=period)
        buy_signals = oscillator < 20
        sell_signals = oscillator > 80
    elif osc_type == 'cci':
        oscillator = calculate_cci(prices, period=period)
        buy_signals = oscillator < -100
        sell_signals = oscillator > 100
    elif osc_type == 'macd':
        macd_line, signal_line = calculate_macd(prices, fast_period=period, slow_period=2*period, signal_period=int(period/2))
        buy_signals = macd_line > signal_line
        sell_signals = macd_line < signal_line
    elif osc_type == 'williamsr':
        oscillator = calculate_williams_r(prices, period=period)
        buy_signals = oscillator < -80
        sell_signals = oscillator > -20
    else:
        raise ValueError("Oscillator type not supported.")
    
    return buy_signals, sell_signals

# Function to evaluate the strategy
def evaluate_strategy(prices, highs, lows, period, osc_type='rsi', initial_cash=10000):
    buy_signals, sell_signals = oscillator_strategy(prices, highs, lows, period, osc_type)
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

# Define the list of oscillator types
osc_types = ['rsi', 'stochastic', 'cci', 'macd', 'williamsr']

# Prompt user for the oscillator type
print("Available oscillators:")
for i, osc_type in enumerate(osc_types, 1):
    print(f"{i}. {osc_type.upper()}")
try:
    selected_osc_type_index = int(input("Enter the number of the oscillator you'd like to test: ").strip()) - 1
    selected_osc_type = osc_types[selected_osc_type_index]
except (ValueError, IndexError):
    print("Invalid input. Please enter a valid number corresponding to the oscillator.")
    exit()

# Prompt user for the range of oscillator parameters
osc_range_start = int(input(f"Enter the start of the {selected_osc_type.upper()} period range (e.g., 5): ").strip())
osc_range_end = int(input(f"Enter the end of the {selected_osc_type.upper()} period range (e.g., 50): ").strip())

# Define the range of oscillator parameters to test
osc_range = range(osc_range_start, osc_range_end + 1)
results = []

# Perform grid search to find the best parameters
for period in osc_range:
    final_value = evaluate_strategy(prices, highs, lows, period, osc_type=selected_osc_type)
    results.append({"Oscillator": selected_osc_type, "Period": period, "Final Value": final_value})

# Convert the results into a DataFrame
results_df = pd.DataFrame(results)

# Find the best parameters
best_parameters = results_df.loc[results_df['Final Value'].idxmax()]

print("Best Parameters:")
print(best_parameters)

# Plotting
fig, ax = plt.subplots()
sc = ax.scatter(results_df['Period'], results_df['Final Value'], label=f'{selected_osc_type.upper()} Oscillator', cmap='viridis', alpha=0.6)
plt.colorbar(sc, ax=ax, label='Final Portfolio Value')
ax.set_xlabel('Period')
ax.set_ylabel('Final Portfolio Value')
ax.set_title('Optimization Results of Oscillator Parameters')
ax.legend(title='Oscillator Type')
plt.show()
