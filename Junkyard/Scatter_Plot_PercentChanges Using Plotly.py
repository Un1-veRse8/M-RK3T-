import yfinance as yf
import pandas as pd
import plotly.express as px

def fetch_data(ticker, period='10y'):
    data = yf.download(ticker, period=period)
    return data

def calculate_percentage_change(data, column):
    return data[column].pct_change().dropna()

def create_interactive_scatter_plot(ticker1, ticker2, period='10y', column1='Adj Close', column2='Adj Close'):
    # Fetch data
    data1 = fetch_data(ticker1, period)
    data2 = fetch_data(ticker2, period)
    
    # Calculate percentage changes
    pct_change1 = calculate_percentage_change(data1, column1)
    pct_change2 = calculate_percentage_change(data2, column2)
    
    # Combine data into a single DataFrame
    combined_data = pd.DataFrame({ticker1: pct_change1, ticker2: pct_change2}).dropna()
    combined_data['Date'] = combined_data.index
    
    # Create interactive scatter plot
    fig = px.scatter(combined_data, x=ticker1, y=ticker2, hover_data=['Date'], 
                     title=f'Scatter Plot: {ticker1} ({column1}) vs {ticker2} ({column2}) ({period})',
                     labels={ticker1: f'{ticker1} Percentage Change ({column1})', ticker2: f'{ticker2} Percentage Change ({column2})'})
    
    fig.show()

# User inputs
ticker1 = input("Enter the first ticker (e.g., 'SPY'): ") or 'SPY'
ticker2 = input("Enter the second ticker (e.g., '^VIX'): ") or '^VIX'
period = input("Enter the historical look-back period (e.g., '10y'): ") or '10y'
column1 = input(f"Enter the data column to use for {ticker1} (Open, High, Low, Close, Adj Close): ") or 'Adj Close'
column2 = input(f"Enter the data column to use for {ticker2} (Open, High, Low, Close, Adj Close): ") or 'Adj Close'

# Create interactive scatter plot with user-defined settings
create_interactive_scatter_plot(ticker1, ticker2, period, column1, column2)
