import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

def scenario_based_simulation(stock_symbol, start_year, num_simulations, num_days, scenario='neutral'):
    end_date = yf.download(stock_symbol).index[-1].strftime('%Y-%m-%d')
    start_date = f'{start_year}-01-01'
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    daily_returns = stock_data['Adj Close'].pct_change().dropna()

    mean_return = daily_returns.mean()
    std_return = daily_returns.std()

    if scenario == 'bullish':
        mean_return += std_return
    elif scenario == 'bearish':
        mean_return -= std_return

    drift = mean_return - (0.5 * std_return**2)
    daily_volatility = std_return

    simulations = np.zeros((num_simulations, num_days))

    for i in range(num_simulations):
        returns = np.random.normal(drift, daily_volatility, num_days)
        simulations[i, :] = returns

    plt.figure(figsize=(10, 6))
    plt.plot(np.cumsum(simulations, axis=1).T, alpha=0.1, color='blue')
    plt.plot(np.cumsum(np.mean(simulations, axis=0)), color='red', linewidth=2, label='Average Simulation')
    plt.title(f'{scenario.capitalize()} Scenario Monte Carlo Simulations of {stock_symbol} Percentage Returns')
    plt.xlabel('Days')
    plt.ylabel('Cumulative Percentage Return')
    plt.legend()
    plt.show()

    final_returns = simulations[:, -1]
    print_simulation_stats(final_returns)

# Example usage
ticker = input("Enter ticker symbol (e.g., ^VIX): ")
start_year = input("Enter start year (e.g., 2017): ")
scenario = input("Enter scenario (bullish, bearish, neutral): ")
scenario_based_simulation(stock_symbol=ticker, start_year=start_year, num_simulations=1000, num_days=252, scenario=scenario)
