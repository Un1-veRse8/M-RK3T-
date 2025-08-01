import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def fetch_data(stock_symbol, start_year):
    end_date = yf.download(stock_symbol).index[-1].strftime('%Y-%m-%d')
    start_date = f'{start_year}-01-01'
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    return stock_data

def generate_signals(data, ma_length):
    data[f'{ma_length}MA'] = data['Adj Close'].rolling(window=ma_length).mean()
    data['Buy_Signal'] = (data['Adj Close'] < 13.5) & (data['Adj Close'] > data[f'{ma_length}MA'])
    return data

def evaluate_strategy(data):
    buy_signals = data[data['Buy_Signal']]
    returns = (buy_signals['Adj Close'].pct_change().dropna() + 1).prod() - 1
    return returns

# Get user inputs
ticker = input("Enter ticker symbol (e.g., ^VIX): ")
start_year = input("Enter start year (e.g., 2017): ")

# Fetch data
vix_data = fetch_data(ticker, start_year)

# Test different moving average lengths
ma_lengths = range(5, 201)
results = []

for length in ma_lengths:
    temp_data = vix_data.copy()
    temp_data = generate_signals(temp_data, length)
    result = evaluate_strategy(temp_data)
    results.append((length, result))

# Convert results to DataFrame
results_df = pd.DataFrame(results, columns=['MA_Length', 'Return'])

# Plot the results
plt.figure(figsize=(12, 6))
plt.plot(results_df['MA_Length'], results_df['Return'], marker='o')
plt.title(f'Strategy Returns for Different Moving Average Lengths for {ticker}')
plt.xlabel('Moving Average Length')
plt.ylabel('Total Return')
plt.grid(True)
plt.show()

# Find the best moving average length
best_ma_length = results_df.loc[results_df['Return'].idxmax()]['MA_Length']
print(f'The best moving average length for {ticker} is {best_ma_length} with a return of {results_df["Return"].max():.2%}')
