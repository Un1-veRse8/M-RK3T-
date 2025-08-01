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

    options['expirationDate'] = pd.to_datetime(options['expirationDate'])
    options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days
    options['CALL'] = options['contractSymbol'].str[4:].apply(lambda x: "C" in x)
    options[['bid', 'ask', 'strike', 'openInterest']] = options[['bid', 'ask', 'strike', 'openInterest']].apply(pd.to_numeric)
    options = options.drop(columns=['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])

    return options, current_price

def is_third_friday(date):
    """Check if a given date is the third Friday of the month."""
    first_day = datetime.date(date.year, date.month, 1)
    first_friday = first_day + datetime.timedelta(days=(4 - first_day.weekday() + 7) % 7)
    third_friday = first_friday + datetime.timedelta(weeks=2)
    return date.date() == third_friday

symbol = input("Enter the stock symbol: ").strip()
try:
    options_data, current_price = options_chain(symbol)
except yfinance.exceptions.YFinanceException as e:
    print(f"An error occurred: {e}. Please check the stock symbol and try again.")
else:
    expiration_dates = options_data['expirationDate'].unique()
    for expiration in expiration_dates:
        num_contracts = options_data[options_data['expirationDate'] == expiration].shape[0]
        calls_open_interest = options_data[(options_data['expirationDate'] == expiration) & (options_data['CALL'] == True)]['openInterest'].sum()
        puts_open_interest = options_data[(options_data['expirationDate'] == expiration) & (options_data['CALL'] == False)]['openInterest'].sum()
        delta_open_interest = abs(calls_open_interest - puts_open_interest)
        dominant = 'C' if calls_open_interest > puts_open_interest else 'P'
        opex_label = " (Monthly OPEX)" if is_third_friday(expiration) else ""
        print(f"Expiration Date: {expiration.date()}{opex_label}, Number of Contracts: {num_contracts}, Calls Open Interest: {calls_open_interest}, Puts Open Interest: {puts_open_interest}, Delta: +{delta_open_interest}{dominant}")
        
    option_type = input("Display open interest for Calls, Puts or Both? (Enter 'Call', 'Put', or 'Both'): ")
    if current_price is not None:
        # Aggregate open interest data
        open_interest_data = options_data.groupby(['strike', 'dte'])['openInterest'].sum().reset_index()

        # Filter based on option type
        if option_type == 'Call':
            open_interest_data = options_data[options_data['CALL'] == True].groupby(['strike', 'dte'])['openInterest'].sum().reset_index()
        elif option_type == 'Put':
            open_interest_data = options_data[options_data['CALL'] == False].groupby(['strike', 'dte'])['openInterest'].sum().reset_index()
        else:
            open_interest_data = options_data.groupby(['strike', 'dte'])['openInterest'].sum().reset_index()

        # Prepare data for plotting
        strikes = open_interest_data['strike']
        days_to_expiration = open_interest_data['dte']
        open_interests = open_interest_data['openInterest']

        # Create the 3D plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plot the surface
        surf = ax.plot_trisurf(days_to_expiration, strikes, open_interests, cmap='viridis', edgecolor='none')

        # Add labels
        ax.set_xlabel('Days to Expiration (DTE)')
        ax.set_ylabel('Strike Price')
        ax.set_zlabel('Open Interest')
        ax.set_title(f'Open Interest Surface for {symbol}')

        # Add watermark
        fig.text(0.5, 0.5, '@o5341V', fontsize=50, color='gray', ha='center', va='center', alpha=0.5, rotation=30)

        # Show the plot
        plt.show()
    else:
        print("Plot not generated due to lack of current price data.")
