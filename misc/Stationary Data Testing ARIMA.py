import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from pmdarima import auto_arima


# Fetch S&P 500 data
def fetch_sp500_data():
    """
    Fetch historical S&P 500 data from Yahoo Finance.
    """
    sp500 = yf.Ticker("^GSPC")
    df = sp500.history(period="max")
    df.reset_index(inplace=True)
    df = df[['Date', 'Close']]
    df.rename(columns={'Date': 'date', 'Close': 'value'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    return df


# Plot time series
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


# Fetch and preprocess data
sp500_data = fetch_sp500_data()
sp500_data.set_index('date', inplace=True)

# Step 1: Plot Original Data
plot_time_series(sp500_data.reset_index(), 'value', "S&P 500 Historical Data (Non-Stationary)", "Index Value")

# Step 2: Apply Log Transformation
sp500_data['log_value'] = np.log(sp500_data['value'])
plot_time_series(sp500_data.reset_index(), 'log_value', "Log-Transformed S&P 500 Data", "Log(Index Value)")

# Step 3: Apply Differencing
sp500_data['log_diff'] = sp500_data['log_value'].diff()
plot_time_series(sp500_data.reset_index(), 'log_diff', "Log Differenced S&P 500 Data", "Differenced Log(Index Value)")

# Step 4: Seasonal Decomposition
print("\nPerforming Seasonal Decomposition...")
decomposition = seasonal_decompose(sp500_data['log_value'].dropna(), model='additive', period=252)  # Approx. 1 year
decomposition.plot()
plt.show()

# Residual Analysis
plot_time_series(decomposition.resid.reset_index(), 'resid', "Residual Component (Stationary)", "Residual Value")

# Step 5: Auto ARIMA
print("\nFinding the best ARIMA model using Auto ARIMA...")
auto_model = auto_arima(
    sp500_data['log_value'].dropna(),
    seasonal=False,  # Set to True for seasonal ARIMA
    stepwise=True,
    trace=True,  # Prints the progress of the model search
    error_action="ignore",  # Ignores errors and keeps searching
    suppress_warnings=True,  # Suppresses warnings
    max_order=None,  # Search for the best p, d, q
)

# Print the selected ARIMA model
print(f"\nBest ARIMA model found: {auto_model.order}")

# Step 6: Fit the Best ARIMA Model
print(f"\nFitting ARIMA{auto_model.order} model...")
model_fit = auto_model.fit(sp500_data['log_value'].dropna())

# Step 7: Forecasting
forecast_steps = int(input("\nEnter the number of steps to forecast: "))
forecast = model_fit.predict(n_periods=forecast_steps)

# Forecast Index
forecast_index = pd.date_range(start=sp500_data.index[-1], periods=forecast_steps + 1, freq='B')[1:]
forecast_df = pd.DataFrame({'date': forecast_index, 'forecast': forecast})
forecast_df.set_index('date', inplace=True)

# Plot Forecast (Log Scale)
plt.figure(figsize=(12, 6))
plt.plot(sp500_data['log_value'], label="Log-Transformed Historical Data", color="blue")
plt.plot(forecast_df['forecast'], label="ARIMA Forecast", color="orange")
plt.title("S&P 500 Forecast with ARIMA (Log Scale)")
plt.xlabel("Date")
plt.ylabel("Log(Index Value)")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# Convert Forecast Back to Original Scale
forecast_original = np.exp(forecast_df['forecast'])

# Plot Forecast (Original Scale)
plt.figure(figsize=(12, 6))
plt.plot(sp500_data['value'], label="Historical Data (Original Scale)", color="blue")
plt.plot(forecast_original, label="ARIMA Forecast (Original Scale)", color="orange")
plt.title("S&P 500 Forecast with ARIMA (Original Scale)")
plt.xlabel("Date")
plt.ylabel("Index Value")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
