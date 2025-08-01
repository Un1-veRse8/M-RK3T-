import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import os

def options_chain(symbol):
    tk = yf.Ticker(symbol)
    try:
        current_price = tk.info['regularMarketPrice']
    except KeyError:
        if 'previousClose' in tk.info:
            current_price = tk.info['previousClose']
        else:
            current_price = None
            print("Warning: No price data available for this symbol.")
    
    exps = tk.options
    if not exps:
        raise ValueError("No options data found for this symbol.")

    options = pd.DataFrame()
    for e in exps:
        opt = tk.option_chain(e)
        opt_combined = pd.concat([opt.calls, opt.puts])
        opt_combined['expirationDate'] = e
        options = pd.concat([options, opt_combined], ignore_index=True)

    options['expirationDate'] = pd.to_datetime(options['expirationDate']) + datetime.timedelta(days=1)
    options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days / 365
    options['CALL'] = options['contractSymbol'].str[4:].apply(lambda x: "C" in x)
    options[['bid', 'ask', 'strike', 'openInterest']] = options[['bid', 'ask', 'strike', 'openInterest']].apply(pd.to_numeric)
    options['date_collected'] = datetime.datetime.now()  # Track when data was collected
    return options, current_price

def store_data(options_data, symbol):
    directory = "/Users/seana/OneDrive/Desktop/Tracking_OI"  # Specify your directory path here
    filename = f"{directory}/{symbol}_options_data.csv"
    if os.path.exists(filename):
        options_data.to_csv(filename, mode='a', header=False, index=False)
    else:
        options_data.to_csv(filename, mode='w', header=True, index=False)

# Example of how to call the function
symbol = input("Enter the stock symbol: ")
options_data, current_price = options_chain(symbol)

# Store data
store_data(options_data, symbol)

if current_price is not None:
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    plt.figure(figsize=(10, 5))
    # Filter and plot data
    calls = options_data[options_data['CALL'] == True]
    puts = options_data[options_data['CALL'] == False]
    plt.bar(calls['strike'], calls['openInterest'], width=1, color='blue', label='Calls', alpha=0.5)
    plt.bar(puts['strike'], puts['openInterest'], width=1, color='red', label='Puts', alpha=0.5)
    plt.axvline(x=current_price, color='green', linestyle='dashed', linewidth=1, label='Current Price')
    plt.title(f'Open Interest across All Strike Prices for {symbol} as of {today_date}')
    plt.xlabel('Strike Price')
    plt.ylabel('Open Interest')
    plt.legend()
    plt.grid(True)
    plt.show()
else:
    print("Plot not generated due to lack of current price data.")
