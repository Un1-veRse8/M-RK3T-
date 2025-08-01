import pandas as pd
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def load_data():
    # Define the ticker symbol and the date range
    ticker = "^GSPC"  # S&P 500 ticker symbol
    end_date = datetime.now()
    start_date = datetime(end_date.year - 20, end_date.month, end_date.day)
    
    try:
        # Load data using yfinance
        df = yf.download(ticker, start=start_date, end=end_date)
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        print("Failed to download data:", e)
        return pd.DataFrame()

def prepare_data(df, start_year):
    # Filter data for the specified range
    df = df[df['Date'].dt.year >= start_year]
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    # Calculate daily returns
    df['Daily Return'] = df['Adj Close'].pct_change()
    # Pivot table to arrange the data into a 2D grid (month x day)
    pivot_table = df.pivot_table(index='Month', columns='Day', values='Daily Return', aggfunc='mean')
    return pivot_table

def plot_heatmap(data, cmap):
    plt.figure(figsize=(15, 10))
    sns.heatmap(data, annot=True, cmap=cmap, fmt=".2%", linewidths=.5, annot_kws={'size': 5})
    plt.title('S&P 500 Seasonality Heatmap')
    plt.xlabel('Day of Month')
    plt.ylabel('Month')
    plt.show()

def spx_seasonality(years_of_data):
    df = load_data()
    if df.empty:
        print("Data loading is not properly implemented. Load your SPX data first.")
        return
    
    start_year = datetime.now().year - years_of_data
    prepared_data = prepare_data(df, start_year)
    
    # Plotting with different color maps
    print("Displaying heatmap with viridis color map:")
    plot_heatmap(prepared_data, 'viridis') # viridis, magma, rocket/rocket_r, flare, mako, Spectral, plasma, inferno


# Example usage:
spx_seasonality(25)  # Adjust the number of years as needed
