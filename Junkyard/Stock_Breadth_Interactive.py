import plotly.graph_objs as go
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Function to fetch stock data
def fetch_stock_data(tickers, start_date, end_date):
    stock_data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return stock_data

# Function to calculate 1-day percentage price changes
def calculate_daily_returns(stock_data):
    daily_returns = stock_data.pct_change(fill_method=None).dropna()
    return daily_returns

# Function to plot interactive KDEs with S&P 500 performance
def plot_interactive_kdes(daily_returns, sp500_returns, days_back):
    dates = daily_returns.index[-days_back:]
    
    fig = go.Figure()

    for date in dates:
        daily_changes = daily_returns.loc[date]
        sp500_change = sp500_returns.loc[date]
        color = 'green' if sp500_change > 0 else 'red'

        kde = go.Histogram(x=daily_changes, histnorm='probability density', marker_color=color, opacity=0.7)
        fig.add_trace(kde)
        
        mean = daily_changes.mean()
        std_dev = daily_changes.std()
        
        fig.add_vline(x=mean, line=dict(color='blue', dash='dash'))
        fig.add_vline(x=mean + std_dev, line=dict(color='orange', dash='dash'))
        fig.add_vline(x=mean - std_dev, line=dict(color='orange', dash='dash'))
        
        fig.add_annotation(xref='paper', yref='paper', x=-0.1, y=0.5, showarrow=False,
                           text=f"Date: {date.date()}", font=dict(size=10), bordercolor=color)
    
    fig.update_layout(
        title="Stock Daily Returns KDE",
        xaxis_title="1-Day % Price Change",
        yaxis_title="Density",
        showlegend=False
    )
    
    fig.show()

if __name__ == "__main__":
    mag_7_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA"]
    days_back = int(input("Enter the number of days back for the plots: "))
    use_all_500 = input("Do you want to use all 500 names in the S&P 500 index? (yes/no): ").strip().lower() == 'yes'
    
    if use_all_500:
        sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
        tickers = sp500_tickers
    else:
        tickers = mag_7_tickers

    sp500_ticker = "^GSPC"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    stock_data = fetch_stock_data(tickers, start_date, end_date)
    sp500_data = fetch_stock_data([sp500_ticker], start_date, end_date)
    
    if stock_data.empty or sp500_data.empty:
        print("No data available for the given date range.")
    else:
        daily_returns = calculate_daily_returns(stock_data)
        sp500_returns = calculate_daily_returns(sp500_data)
        plot_interactive_kdes(daily_returns, sp500_returns, days_back)
