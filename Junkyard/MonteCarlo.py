import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# Fetch historical data
symbol = 'AAPL'
data = yf.download(symbol, start='2010-01-01', end='2023-01-01')
data['Return'] = data['Adj Close'].pct_change().fillna(0)

# Parameters
sims = 100  # Number of simulations
steps = 252  # Days in a simulated year

# Initialize DataFrame to store simulation results
simulation_df = pd.DataFrame()

# Generate simulated price paths
np.random.seed(0)  # for reproducibility
for i in range(sims):
    prices = [data['Adj Close'].iloc[-1]]  # Start with the last known price
    for d in range(1, steps):
        # Apply daily return to the previous price
        daily_return = np.random.normal(data['Return'].mean(), data['Return'].std())
        prices.append(prices[-1] * (1 + daily_return))
    
    simulation_df[i] = prices

# Applying Buy and Hold Strategy
# In this simple strategy, just hold the initial price, so the portfolio value is directly reflected by the price paths.

# Plot the results
plt.figure(figsize=(14, 7))
for i in simulation_df.columns:
    plt.plot(simulation_df.index, simulation_df[i], lw=1, alpha=0.5)  # Plot each simulation path

plt.title(f'Monte Carlo Simulation of {symbol} - Buy and Hold Strategy')
plt.xlabel('Days')
plt.ylabel('Price')
plt.show()
