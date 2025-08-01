import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

# User inputs for stock symbol and number of years back to check
symbol = input("Enter the stock symbol (e.g., 'AAPL'): ").strip()
years_back = int(input("Enter the number of years back to analyze (e.g., 1, 2, 3,...): "))

# Calculate start and end dates based on user input
end_date = datetime.now().date()
start_date = end_date - timedelta(days=252 * years_back)

# Fetching the data
data = yf.download(symbol, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

# Fetch the most recent data separately to ensure it includes the latest date
recent_data = yf.download(symbol, period="1d")

# Ensure data is loaded
if data.empty or recent_data.empty:
    print("No data fetched. Check the stock symbol or network connection.")
else:
    # Append the most recent data to the existing data
    data = pd.concat([data, recent_data]).drop_duplicates()

    # Calculate daily returns as percentage changes
    data['Daily Return'] = data['Adj Close'].pct_change() * 100
    data.dropna(subset=['Volume'], inplace=True)  # Remove any NaN values in volume

    # Print the last few rows of data for verification
    print("Last few rows of data for verification:")
    print(data.tail())

    # Calculate future returns for various days
    days_list = [5, 10, 21, 63, 126, 252]  # Added 126 days
    for days in days_list:
        data[f'Return_{days}_days'] = data['Adj Close'].pct_change(periods=-days) * 100

    # Verify the recent volume and closing price
    recent_volume = data['Volume'].iloc[-1]
    recent_close = data['Adj Close'].iloc[-1]
    print(f"Recent volume: {recent_volume}, Recent close: {recent_close}")

    # Filter out rows where future returns could not be calculated
    future_returns_data = data.dropna(subset=[f'Return_{days}_days' for days in days_list])

    # Get the latest data point with sufficient data for future returns
    if not future_returns_data.empty:
        latest_returns = {days: future_returns_data[f'Return_{days}_days'].iloc[-1] for days in days_list}
    else:
        latest_returns = {days: None for days in days_list}

    # Verify the latest data point
    print(f"Latest returns: {latest_returns}")

    # Plotting
    fig, axes = plt.subplots(3, 2, figsize=(14, 18), sharex=True)
    axes = axes.flatten()
    for i, days in enumerate(days_list):
        scatter = axes[i].scatter(future_returns_data['Volume'], future_returns_data[f'Return_{days}_days'], alpha=0.5, label=f'Vol vs Return after {days} days')
        axes[i].set_xlabel('Volume (Millions)')
        axes[i].set_ylabel(f'Return After {days} Days (%)')
        axes[i].grid(True)

        # Format x-axis to show volume in millions
        axes[i].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x/1e6))))

        # Linear regression on each subset
        X = future_returns_data['Volume'].values.reshape(-1, 1)  # Volume as independent variable
        y = future_returns_data[f'Return_{days}_days'].values  # Future returns as dependent variable
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        regression_line, = axes[i].plot(future_returns_data['Volume'], y_pred, color='red', linewidth=2, label='Regression Line')  # Plot regression line

        # Adding a text watermark to each subplot
        axes[i].text(0.5, 0.5, 'o5341V', fontsize=20, color='gray', ha='center', va='center', alpha=0.5, transform=axes[i].transAxes)

        # Add a crosshair at the latest data point
        axes[i].axvline(x=recent_volume, color='green', linestyle='--', lw=0.5)
        axes[i].axhline(y=latest_returns[days], color='green', linestyle='--', lw=0.5)
        axes[i].text(recent_volume, latest_returns[days], f'({recent_volume/1e6:.2f}M, {latest_returns[days]:.2f}%)' if latest_returns[days] is not None else '',
                     fontsize=10, ha='left', va='bottom', color='black')

        # Add legend
        axes[i].legend(handles=[scatter, regression_line])

    fig.tight_layout(pad=2.0)
    plt.show()

print("https://twitter.com/o5341V")