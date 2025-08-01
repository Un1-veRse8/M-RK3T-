import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model

def garch_monte_carlo_simulation(stock_symbol, start_year, num_simulations, num_days):
    end_date = yf.download(stock_symbol).index[-1].strftime('%Y-%m-%d')
    start_date = f'{start_year}-01-01'
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    daily_returns = stock_data['Adj Close'].pct_change().dropna()

    garch_model = arch_model(daily_returns, vol='Garch', p=1, q=1)
    garch_fitted = garch_model.fit(disp='off')
    forecast = garch_fitted.forecast(horizon=num_days)
    mean_forecast = forecast.mean.values[-1, :]
    variance_forecast = forecast.variance.values[-1, :]
    std_forecast = np.sqrt(variance_forecast)

    simulations = np.zeros((num_simulations, num_days))

    for i in range(num_simulations):
        returns = np.random.normal(mean_forecast, std_forecast)
        simulations[i, :] = returns

    plt.figure(figsize=(10, 6))
    plt.plot(np.cumsum(simulations, axis=1).T, alpha=0.1, color='blue')
    plt.plot(np.cumsum(np.mean(simulations, axis=0)), color='red', linewidth=2, label='Average Simulation')
    plt.title(f'GARCH Monte Carlo Simulations of {stock_symbol} Percentage Returns')
    plt.xlabel('Days')
    plt.ylabel('Cumulative Percentage Return')
    plt.legend()
    plt.show()

    final_returns = simulations[:, -1]
    print_simulation_stats(final_returns)

# Example usage
ticker = input("Enter ticker symbol (e.g., ^VIX): ")
start_year = input("Enter start year (e.g., 2017): ")
garch_monte_carlo_simulation(stock_symbol=ticker, start_year=start_year, num_simulations=1000, num_days=252)
