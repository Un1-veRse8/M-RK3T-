import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

def jump_diffusion_monte_carlo_simulation(stock_symbol, start_year, num_simulations, num_days, jump_lambda=0.1, jump_sigma=0.02):
    end_date = yf.download(stock_symbol).index[-1].strftime('%Y-%m-%d')
    start_date = f'{start_year}-01-01'
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    daily_returns = stock_data['Adj Close'].pct_change().dropna()

    mean_return = daily_returns.mean()
    std_return = daily_returns.std()
    drift = mean_return - (0.5 * std_return**2)
    daily_volatility = std_return

    simulations = np.zeros((num_simulations, num_days))

    for i in range(num_simulations):
        returns = np.random.normal(drift, daily_volatility, num_days)
        jumps = np.random.normal(0, jump_sigma, num_days) * (np.random.uniform(0, 1, num_days) < jump_lambda)
        returns += jumps
        simulations[i, :] = returns

    plt.figure(figsize=(10, 6))
    plt.plot(np.cumsum(simulations, axis=1).T, alpha=0.1, color='blue')
    plt.plot(np.cumsum(np.mean(simulations, axis=0)), color='red', linewidth=2, label='Average Simulation')
    plt.title(f'Jump Diffusion Monte Carlo Simulations of {stock_symbol} Percentage Returns')
    plt.xlabel('Days')
    plt.ylabel('Cumulative Percentage Return')
    plt.legend()
    plt.show()

    final_returns = simulations[:, -1]
    print_simulation_stats(final_returns)

# Example usage
ticker = input("Enter ticker symbol (e.g., ^VIX): ")
start_year = input("Enter start year (e.g., 2017): ")
jump_diffusion_monte_carlo_simulation(stock_symbol=ticker, start_year=start_year, num_simulations=1000, num_days=252, jump_lambda=0.1, jump_sigma=0.02)
