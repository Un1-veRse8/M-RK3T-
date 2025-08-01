import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def fetch_data(ticker, period='10y'):
    data = yf.download(ticker, period=period)
    return data

def calculate_percentage_change(data, column):
    return data[column].pct_change().dropna()

def create_scatter_plot_with_annotations(ticker1, ticker2, period='10y', column1='Adj Close', column2='Adj Close', threshold=0.05):
    # Fetch data
    data1 = fetch_data(ticker1, period)
    data2 = fetch_data(ticker2, period)
    
    # Calculate percentage changes
    pct_change1 = calculate_percentage_change(data1, column1)
    pct_change2 = calculate_percentage_change(data2, column2)
    
    # Combine data into a single DataFrame
    combined_data = pd.DataFrame({ticker1: pct_change1, ticker2: pct_change2}).dropna()
    
    # Identify the last data point
    last_data_point = combined_data.iloc[-1]
    
    # Calculate the thresholds
    lower_threshold1 = pct_change1.quantile(threshold)
    upper_threshold1 = pct_change1.quantile(1 - threshold)
    lower_threshold2 = pct_change2.quantile(threshold)
    upper_threshold2 = pct_change2.quantile(1 - threshold)
    
    # Filter data points based on thresholds
    significant_points = combined_data[
        (combined_data[ticker1] <= lower_threshold1) | 
        (combined_data[ticker1] >= upper_threshold1) | 
        (combined_data[ticker2] <= lower_threshold2) | 
        (combined_data[ticker2] >= upper_threshold2)
    ]
    
    # Create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(combined_data[ticker1], combined_data[ticker2], alpha=0.5, label='Data Points')
    plt.scatter(last_data_point[ticker1], last_data_point[ticker2], color='red', label='Last Data Point')
    plt.axvline(x=last_data_point[ticker1], alpha=0.2, color='red', linestyle='--')
    plt.axhline(y=last_data_point[ticker2], alpha=0.2, color='red', linestyle='--')
    
    # Annotate significant points
    for date, row in significant_points.iterrows():
        x, y = row[ticker1], row[ticker2]
        plt.annotate(f'{date.strftime("%Y-%m-%d")}', (x, y), fontsize=8, alpha=0.7,
                     xytext=(5, 5), textcoords='offset points')
    
    # Add watermark
    plt.text(0.5, 0.5, '@o5341V', fontsize=99, color='gray', alpha=0.4,
             ha='center', va='center', rotation=30, transform=plt.gca().transAxes)
    
    plt.title(f'Scatter Plot: {ticker1} ({column1}) vs {ticker2} ({column2}) ({period})')
    plt.xlabel(f'{ticker1} Percentage Change ({column1})')
    plt.ylabel(f'{ticker2} Percentage Change ({column2})')
    plt.legend()
    plt.grid(True)
    plt.show()

# User inputs
ticker1 = input("Enter the first ticker (e.g., 'SPY'): ") or 'SPY'
ticker2 = input("Enter the second ticker (e.g., '^VIX'): ") or '^VIX'
period = input("Enter the historical look-back period (e.g., '10y'): ") or '10y'
column1 = input(f"Enter the data column to use for {ticker1} (Open, High, Low, Close, Adj Close): ") or 'Adj Close'
column2 = input(f"Enter the data column to use for {ticker2} (Open, High, Low, Close, Adj Close): ") or 'Adj Close'
threshold = float(input("Enter the percentage threshold for annotation (e.g., 0.05 for top and bottom 5%): ") or 0.05)

# Create scatter plot with annotations and watermark
create_scatter_plot_with_annotations(ticker1, ticker2, period, column1, column2, threshold)
