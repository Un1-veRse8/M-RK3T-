import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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
    options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days
    options['CALL'] = options['contractSymbol'].str[4:].apply(lambda x: "C" in x)
    options[['bid', 'ask', 'strike', 'volume']] = options[['bid', 'ask', 'strike', 'volume']].apply(pd.to_numeric)
    options = options.drop(columns=['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])

    return options, current_price

symbol = input("Enter the stock symbol: ")
option_type = input("Display volume for Calls, Puts or Both? (Enter 'Call', 'Put', or 'Both'): ")
options_data, current_price = options_chain(symbol)

if current_price is not None:
    # Aggregate volume data
    volume_data = options_data.groupby(['strike', 'dte'])['volume'].sum().reset_index()

    # Filter based on option type
    if option_type == 'Call':
        volume_data = options_data[options_data['CALL'] == True].groupby(['strike', 'dte'])['volume'].sum().reset_index()
    elif option_type == 'Put':
        volume_data = options_data[options_data['CALL'] == False].groupby(['strike', 'dte'])['volume'].sum().reset_index()
    else:
        volume_data = options_data.groupby(['strike', 'dte'])['volume'].sum().reset_index()

    # Prepare data for plotting
    strikes = volume_data['strike']
    days_to_expiration = volume_data['dte']
    volumes = volume_data['volume']

    # Create the 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the surface
    surf = ax.plot_trisurf(days_to_expiration, strikes, volumes, cmap='viridis', edgecolor='none')

    # Add labels
    ax.set_xlabel('Days to Expiration (DTE)')
    ax.set_ylabel('Strike Price')
    ax.set_zlabel('Volume')
    ax.set_title(f'Volume Surface for {symbol}')

    # Add watermark
    fig.text(0.5, 0.5, '@o5341V', fontsize=50, color='gray', ha='center', va='center', alpha=0.5, rotation=30)

    # Show the plot
    plt.show()
else:
    print("Plot not generated due to lack of current price data.")
