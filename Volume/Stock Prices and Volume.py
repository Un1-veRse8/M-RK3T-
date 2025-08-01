import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import numpy as np

# User inputs for stock symbol and number of years back to check
symbol = input("Enter the stock symbol (e.g., 'AAPL'): ").strip()
years_back = int(input("Enter the number of years back to analyze (e.g., 1, 2, 3,...): "))

# Calculate start and end dates based on user input
end_date = datetime.now()
start_date = end_date - timedelta(days=365 * years_back)

# Fetching the data
data = yf.download(symbol, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

# Ensure data is loaded
if data.empty:
    print("No data fetched. Check the stock symbol or network connection.")
else:
    # Calculate daily returns as percentage changes
    data['Daily Return'] = data['Adj Close'].pct_change() * 100
    data['Volume (Millions)'] = data['Volume'] / 1e6  # Simplify volume for better readability
    data.dropna(subset=['Daily Return', 'Volume'], inplace=True)  # Remove any NaN values that arise

    # Prepare data for linear regression
    X = data['Volume (Millions)'].values.reshape(-1, 1)  # Volume as independent variable
    y = data['Daily Return'].values  # Daily returns as dependent variable
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    # Scatter plot with matplotlib
    plt.figure(figsize=(10, 6))
    plt.scatter(data['Volume (Millions)'], data['Daily Return'], alpha=0.5, label='Daily Data')
    plt.plot(data['Volume (Millions)'], y_pred, color='red', linewidth=2, label='Regression Line')  # Plot regression line

    # Highlight the most recent data point and add crosshairs
    recent_data = data.iloc[-1]
    plt.scatter(recent_data['Volume (Millions)'], recent_data['Daily Return'], color='red', s=100, label='Most Recent Data')
    plt.axhline(y=recent_data['Daily Return'], color='green', linestyle='--', linewidth=1)
    plt.axvline(x=recent_data['Volume (Millions)'], color='green', linestyle='--', linewidth=1)

    # Set titles and labels
    plt.title(f'Relationship between Volume and Daily Returns for {symbol}')
    plt.xlabel('Volume (Millions)')
    plt.ylabel('Daily Return (%)')
    plt.legend()
    plt.grid(True)

    # Adding a text watermark
    plt.text(0.5, 0.5, 'o5341V', fontsize=40, color='gray', ha='center', va='center', alpha=0.5, transform=plt.gcf().transFigure)

    plt.show()

    # Output the coefficients
    print(f"Coefficient (Slope): {model.coef_[0]}")
    print(f"Intercept: {model.intercept_}")
