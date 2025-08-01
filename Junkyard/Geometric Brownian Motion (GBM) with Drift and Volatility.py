import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

def gbm_monte_carlo_simulation(stock_symbol, start_year, num_simulations, num_days):
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
        simulations[i, :] = returns

    plt.figure(figsize=(10, 6))
    plt.plot(np.cumsum(simulations, axis=1).T, alpha=0.1, color='blue')
    plt.plot(np.cumsum(np.mean(simulations, axis=0)), color='red', linewidth=2, label='Average Simulation')
    plt.title(f'GBM Monte Carlo Simulations of {stock_symbol} Percentage Returns')
    plt.xlabel('Days')
    plt.ylabel('Cumulative Percentage Return')
    plt.legend()
    plt.show()

    final_returns = simulations[:, -1]
    print_simulation_stats(final_returns)

def print_simulation_stats(final_returns):
    mean_final_return = np.mean(final_returns)
    median_final_return = np.median(final_returns)
    var_95 = np.percentile(final_returns, 5)
    var_99 = np.percentile(final_returns, 1)

    print(f'Mean final return: {mean_final_return:.2f}')
    print(f'Median final return: {median_final_return:.2f}')
    print(f'5th percentile (VaR 95%): {var_95:.2f}')
    print(f'1st percentile (VaR 99%): {var_99:.2f}')

# Example usage
ticker = input("Enter ticker symbol (e.g., ^VIX): ")
start_year = input("Enter start year (e.g., 2017): ")
gbm_monte_carlo_simulation(stock_symbol=ticker, start_year=start_year, num_simulations=1000, num_days=252)
