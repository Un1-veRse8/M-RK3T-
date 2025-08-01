import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

# User inputs for stock symbol and specific year to start analysis
symbol = input("Enter the stock symbol (e.g., 'SPY'): ").strip()
start_year = int(input("Enter the start year for analysis (e.g., 2020): "))
use_ma = input("Would you like to use a moving average of volume? (yes/no): ").strip().lower() == 'yes'
ma_length = int(input("Enter the length of the moving average for volume (e.g., 10, 20): ")) if use_ma else None
filter_volume = input("Would you like to filter the data based on volume threshold? (yes/no): ").strip().lower() == 'yes'
volume_threshold = int(input("Enter the volume threshold in millions (e.g., 60 for 60 million): ")) * 1e6 if filter_volume else None

# Calculate start and end dates based on user input
end_date = datetime.now().date()
start_date = datetime(start_year, 1, 1).date()

# Fetching the data
data = yf.download(symbol, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

# Ensure data is loaded
if data.empty:
    print("No data fetched. Check the stock symbol or network connection.")
else:
    # Calculate daily returns as percentage changes
    data['Daily Return'] = data['Close'].pct_change() * 100
    data.dropna(subset=['Volume'], inplace=True)  # Remove any NaN values in volume

    # Calculate the volume moving average if selected
    if use_ma and ma_length:
        data['Volume_MA'] = data['Volume'].rolling(window=ma_length).mean()
        volume_col = 'Volume_MA'
    else:
        volume_col = 'Volume'

    # Calculate future returns for calendar days
    days_list = [5, 10, 21, 63, 126, 252]  # 1 week, 2 weeks, 1 month, 3 months, 6 months, 1 year
    for days in days_list:
        data[f'Future_Close_{days}_days'] = data['Close'].shift(-days)
        data[f'Return_{days}_days'] = (data[f'Future_Close_{days}_days'] - data['Close']) / data['Close'] * 100

    # Verify the recent volume and closing price
    recent_volume = data[volume_col].iloc[-1]
    recent_close = data['Close'].iloc[-1]
    print(f"Recent volume (or MA of volume): {recent_volume}, Recent close: {recent_close}")

    # Filter out rows where future returns could not be calculated and apply volume threshold if selected
    future_returns_data = data.dropna(subset=[f'Return_{days}_days' for days in days_list] + [volume_col])
    if filter_volume:
        print(f"Data before applying volume filter: {future_returns_data.shape}")
        future_returns_data = future_returns_data[future_returns_data[volume_col] < volume_threshold]
        print(f"Data after applying volume filter: {future_returns_data.shape}")

    # Specific check for March 31, 2020, for verification
    specific_date = '2020-03-31'
    if specific_date in data.index:
        print(f"\nTest Data for {specific_date}:")
        specific_close = data.loc[specific_date, 'Close']
        specific_volume = data.loc[specific_date, 'Volume']
        print(f"Close: {specific_close}, Volume: {specific_volume}")
        for days in days_list:
            return_value = data.loc[specific_date, f'Return_{days}_days']
            future_date = data.index[data.index.get_loc(specific_date) + days]
            future_close = data.loc[future_date, 'Close']
            print(f"Return after {days} days: {return_value:.2f}%, Future Close: {future_close:.2f} on {future_date}")

    # Compute the average return for the most recent volume range
    latest_returns = {}
    volume_ranges = np.linspace(future_returns_data[volume_col].min(), future_returns_data[volume_col].max(), 10)
    for days in days_list:
        volume_min = volume_ranges[np.digitize(recent_volume, volume_ranges) - 1]
        volume_max = volume_ranges[np.digitize(recent_volume, volume_ranges)]
        mask = (future_returns_data[volume_col] >= volume_min) & (future_returns_data[volume_col] < volume_max)
        avg_return = future_returns_data.loc[mask, f'Return_{days}_days'].mean()
        latest_returns[days] = avg_return

    # Compute the average return for the entire filtered dataset
    global_avg_returns = {days: future_returns_data[f'Return_{days}_days'].mean() for days in days_list}

    # Verify the latest data point
    print("\nReturn Avg. for Recent Volume:")
    for days, avg_return in latest_returns.items():
        print(f"Return after {days} days: {avg_return:.2f}%")

    print("\nGlobal Avg. for all Volume:")
    for days, avg_return in global_avg_returns.items():
        print(f"Return after {days} days: {avg_return:.2f}%")

    # Plotting
    fig, axes = plt.subplots(3, 2, figsize=(14, 18), sharex=True)
    axes = axes.flatten()
    for i, days in enumerate(days_list):
        valid_data = future_returns_data.dropna(subset=[f'Return_{days}_days', volume_col])
        if valid_data.empty:
            axes[i].text(0.5, 0.5, f'No valid data for {days} days', fontsize=12, ha='center', va='center')
            continue
        
        scatter = axes[i].scatter(valid_data[volume_col], valid_data[f'Return_{days}_days'], alpha=0.5, label=f'Vol vs Return after {days} days')
        axes[i].set_xlabel('Volume (Millions)' if not use_ma else f'Volume {ma_length}-day MA (Millions)')
        axes[i].set_ylabel(f'Return After {days} Days (%)')
        axes[i].grid(True, alpha=0.3)  # Set gridline transparency

        # Format x-axis to show volume in millions
        axes[i].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x/1e6))))

        # Linear regression on each subset
        X = valid_data[volume_col].values.reshape(-1, 1)  # Volume as independent variable
        y = valid_data[f'Return_{days}_days'].values  # Future returns as dependent variable
        if len(X) > 0 and len(y) > 0:
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)
            regression_line = axes[i].plot(valid_data[volume_col], y_pred, color='red', linewidth=2, label='Regression Line')  # Plot regression line

        # Adding a text watermark to each subplot
        axes[i].text(0.5, 0.5, 'o5341V', fontsize=20, color='gray', ha='center', va='center', alpha=0.5, transform=axes[i].transAxes)

        # Add a crosshair at the average return for the recent volume
        avg_return = latest_returns[days]
        avg_line = axes[i].axvline(x=recent_volume, color='green', linestyle='-', lw=1, label='Return Avg. for Recent Volume')
        avg_hline = axes[i].axhline(y=avg_return, color='green', linestyle='-', lw=1)
        if avg_return is not None:
            axes[i].text(recent_volume, avg_return, f'({recent_volume/1e6:.2f}M, {avg_return:.2f}%)',
                         fontsize=10, ha='left', va='bottom', color='black', zorder=10)

        # Add a crosshair for the global average return
        global_avg_return = global_avg_returns[days]
        global_avg_hline = axes[i].axhline(y=global_avg_return, color='blue', linestyle='--', lw=0.5)
        if global_avg_return is not None:
            axes[i].text(axes[i].get_xlim()[1], global_avg_return, f'Global Avg: {global_avg_return:.2f}%',
                         fontsize=10, ha='right', va='bottom', color='black', zorder=10)

        # Add legend
        if len(X) > 0 and len(y) > 0:
            handles = [avg_line]
        else:
            handles = [scatter]
        axes[i].legend(handles=handles)

        # Set the title for each subplot
        axes[i].set_title(f'Vol vs Return after {days} days')

    fig.suptitle(f'{symbol} Volume vs. Returns Analysis from {start_year} to {end_date.year}', fontsize=16)
    fig.tight_layout(pad=2.0, rect=[0, 0, 1, 0.96])
    plt.show()
