"""
Real-Time Data Visualization Dashboard
Displays live stock prices using Dash and Plotly.
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

# Alpha Vantage API key and endpoint
ALPHA_VANTAGE_API_KEY = "T8VQGBJOOMH4NECO"  # Replace with your Alpha Vantage API key
STOCK_SYMBOL = "AAPL"  # Example: Apple Inc.

# Fetch live data from Alpha Vantage
def fetch_stock_data(symbol):
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    # Parse the response into a DataFrame
    if "Time Series (1min)" in data:
        time_series = data["Time Series (1min)"]
        df = pd.DataFrame.from_dict(time_series, orient="index", dtype=float)
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })
        df.index = pd.to_datetime(df.index)
        return df.sort_index()
    else:
        return pd.DataFrame()

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Real-Time Stock Price Dashboard", style={"textAlign": "center"}),
    html.Div([
        html.Label("Stock Symbol:"),
        dcc.Input(
            id="stock-symbol", 
            type="text", 
            value=STOCK_SYMBOL, 
            debounce=True, 
            placeholder="Enter stock symbol"
        )
    ]),
    dcc.Graph(id="stock-price-graph"),
    dcc.Interval(id="update-interval", interval=60000, n_intervals=0)  # Update every 60 seconds
])

# Callbacks
@app.callback(
    Output("stock-price-graph", "figure"),
    [Input("stock-symbol", "value"),
     Input("update-interval", "n_intervals")]
)
def update_graph(symbol, n_intervals):
    df = fetch_stock_data(symbol)
    if not df.empty:
        figure = {
            "data": [
                go.Scatter(
                    x=df.index,
                    y=df["Close"],
                    mode="lines",
                    name="Close Price"
                )
            ],
            "layout": {
                "title": f"Live Stock Prices for {symbol}",
                "xaxis": {"title": "Time"},
                "yaxis": {"title": "Price (USD)"},
                "template": "plotly_dark"
            }
        }
        return figure
    return {
        "data": [],
        "layout": {"title": "No data available"}
    }

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
