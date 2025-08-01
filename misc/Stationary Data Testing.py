import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose


def fetch_sp500_data():
    """
    Fetch historical S&P 500 data from Yahoo Finance.
    """
    sp500 = yf.Ticker("^GSPC")
    df = sp500.history(period="max")  # Fetch maximum available historical data
    df.reset_index(inplace=True)
    df = df[['Date', 'Close']]
    df.rename(columns={'Date': 'date', 'Close': 'value'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    return df


def test_stationarity(timeseries):
    """
    Perform the Augmented Dickey-Fuller (ADF) test for stationarity.
    """
    result = adfuller(timeseries.dropna())
    print("ADF Statistic:", result[0])
    print("p-value:", result[1])
    print("Critical Values:")
    for key, value in result[4].items():
        print(f"   {key}: {value}")
    if result[1] <= 0.05:
        print("Result: The data is stationary (reject the null hypothesis).")
    else:
        print("Result: The data is non-stationary (fail to reject the null hypothesis).")


def plot_time_series(df, column, title, ylabel):
    """
    Helper function to plot a time series.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df[column], label=title, color="blue")
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()


# Fetch S&P 500 data
sp500_data = fetch_sp500_data()
sp500_data.set_index('date', inplace=True)

# Step 1: Plot Original Data
plot_time_series(sp500_data.reset_index(), 'value', "S&P 500 Historical Data (Non-Stationary)", "Index Value")

# Step 2: Test for Stationarity on Original Data
print("Testing Stationarity for Original Data:")
test_stationarity(sp500_data['value'])

# Step 3: Apply Log Transformation
sp500_data['log_value'] = np.log(sp500_data['value'])
plot_time_series(sp500_data.reset_index(), 'log_value', "Log-Transformed S&P 500 Data", "Log(Index Value)")

# Test Stationarity for Log-Transformed Data
print("\nTesting Stationarity for Log-Transformed Data:")
test_stationarity(sp500_data['log_value'])

# Step 4: Apply Differencing
sp500_data['log_diff'] = sp500_data['log_value'].diff()
plot_time_series(sp500_data.reset_index(), 'log_diff', "Log Differenced S&P 500 Data", "Differenced Log(Index Value)")

# Test Stationarity for Differenced Data
print("\nTesting Stationarity for Differenced Data:")
test_stationarity(sp500_data['log_diff'])

# Step 5: Seasonal Decomposition
print("\nPerforming Seasonal Decomposition...")
decomposition = seasonal_decompose(sp500_data['log_value'].dropna(), model='additive', period=252)  # Approx. 1 year
decomposition.plot()
plt.show()

# Residual Analysis
plot_time_series(decomposition.resid.reset_index(), 'resid', "Residual Component (Stationary)", "Residual Value")
print("\nTesting Stationarity for Residual Component:")
test_stationarity(decomposition.resid)
