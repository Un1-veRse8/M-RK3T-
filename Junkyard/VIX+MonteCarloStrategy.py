import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def fetch_data(stock_symbol, start_year):
    end_date = yf.download(stock_symbol).index[-1].strftime('%Y-%m-%d')
    start_date = f'{start_year}-01-01'
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    return stock_data

def generate_signals(data):
    data['21MA'] = data['Adj Close'].rolling(window=47).mean()
    data['Buy_Signal'] = (data['Adj Close'] < 13.5) & (data['Adj Close'] > data['21MA'])
    return data

def monte_carlo_simulation(data, num_simulations, num_days):
    daily_returns = data['Adj Close'].pct_change().dropna()
    mean_return = daily_returns.mean()
    std_return = daily_returns.std()
    
    simulations = np.zeros((num_simulations, num_days))
    
    for i in range(num_simulations):
        returns = np.random.normal(mean_return, std_return, num_days)
        simulations[i, :] = returns
        
    return simulations

def plot_simulation(data, simulations, ticker):
    plt.figure(figsize=(10, 6))
    plt.plot(np.cumsum(simulations, axis=1).T, alpha=0.1, color='blue')
    plt.plot(np.cumsum(np.mean(simulations, axis=0)), color='red', linewidth=2, label='Average Simulation')
    plt.title(f'{ticker} Monte Carlo Simulations with Strategy')
    plt.xlabel('Days')
    plt.ylabel('Cumulative Percentage Return')
    plt.legend()
    plt.show()

def evaluate_strategy(data):
    buy_signals = data[data['Buy_Signal']]
    returns = (buy_signals['Adj Close'].pct_change().dropna() + 1).prod() - 1
    print(f'Total Return from Strategy: {returns:.2%}')

# Example usage
ticker = "^VIX"
start_year = 1900
vix_data = fetch_data(ticker, start_year)
vix_data = generate_signals(vix_data)
num_simulations = 1000
num_days = 252
simulations = monte_carlo_simulation(vix_data, num_simulations, num_days)
plot_simulation(vix_data, simulations, ticker)
evaluate_strategy(vix_data)
