import yfinance as yf
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

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
    data['Predicted Return'] = model.predict(X)

    # Create interactive scatter plot with Plotly
    fig = px.scatter(data, x='Volume (Millions)', y='Daily Return',
                     hover_data={'Volume (Millions)': ':.2f', 'Daily Return': ':.2f'},
                     title=f'Relationship between Volume and Daily Returns for {symbol}')
    fig.add_scatter(x=data['Volume (Millions)'], y=data['Predicted Return'], mode='lines', name='Regression Line')

    # Highlight the most recent data point
    recent_data = data.iloc[-1]
    fig.add_shape(type="line",
                  x0=recent_data['Volume (Millions)'], y0=min(data['Daily Return']), x1=recent_data['Volume (Millions)'], y1=max(data['Daily Return']),
                  line=dict(color="RoyalBlue", width=2))
    fig.add_shape(type="line",
                  x0=min(data['Volume (Millions)']), y0=recent_data['Daily Return'], x1=max(data['Volume (Millions)']), y1=recent_data['Daily Return'],
                  line=dict(color="RoyalBlue", width=2))

    # Add watermark
    fig.add_annotation(x=0.5, y=0.5, text="o5341V", showarrow=False, font=dict(size=20, color="gray"), opacity=0.5, xref="paper", yref="paper")

    fig.show()

    # Output the coefficients
    print(f"Coefficient (Slope): {model.coef_[0]}")
    print(f"Intercept: {model.intercept_}")
