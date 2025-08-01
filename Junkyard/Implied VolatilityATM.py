import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FixedLocator

def fetch_atm_iv_data(symbol):
    tk = yf.Ticker(symbol)
    exps = tk.options
    if not exps:
        print("No options data available.")
        return None

    iv_data = []
    try:
        current_price = tk.history(period="1d")['Close'].iloc[-1]
    except IndexError:
        print("Failed to fetch current price.")
        return None

    for exp in exps:
        opt = tk.option_chain(exp)
        calls = opt.calls
        puts = opt.puts
        
        # Concatenate call and put data
        options = pd.concat([calls, puts])

        # Find the closest strike to the current price
        closest_strike = options['strike'].iloc[(options['strike'] - current_price).abs().argmin()]

        # Selecting the rows that match the closest_strike
        atm_options = options[options['strike'] == closest_strike]

        for index, row in atm_options.iterrows():
            iv_data.append({
                'Date': exp,
                'IV': row['impliedVolatility'] * 100,
                'Type': 'Call' if 'C' in row['contractSymbol'] else 'Put'
            })

    return pd.DataFrame(iv_data)

def plot_iv_over_time(iv_data, option_type):
    # Convert 'Date' to matplotlib date numbers
    iv_data['Date'] = pd.to_datetime(iv_data['Date'])
    iv_data['Date'] = mdates.date2num(iv_data['Date'])  # Converting to matplotlib date format

    plt.figure(figsize=(12, 6))
    
    # Determine which types to plot
    types_to_plot = ['Call', 'Put'] if option_type == "Both" else [option_type]
    for t in types_to_plot:
        filtered_data = iv_data[iv_data['Type'] == t]
        if not filtered_data.empty:
            plt.plot(filtered_data['Date'], filtered_data['IV'], label=f'{t} IV', marker='o', linestyle='-')

    # Setting custom x-axis ticks
    unique_dates = iv_data['Date'].drop_duplicates().sort_values()
    plt.gca().xaxis.set_major_locator(FixedLocator(unique_dates))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Adding a text watermark
    plt.text(0.5, 0.5, 'o5341V', fontsize=40, color='gray', ha='center', va='center', alpha=0.5, transform=plt.gca().transAxes)

    plt.title('Implied Volatility Over Time for ATM Strikes')
    plt.xlabel('Expiration Date')
    plt.ylabel('Implied Volatility (%)')
    plt.xticks(rotation=90)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Main execution
symbol = input("Enter the stock symbol: ")
option_type = input("Display IV for Calls, Puts or Both? (Enter 'Call', 'Put', or 'Both'): ")
iv_data = fetch_atm_iv_data(symbol)
if iv_data is not None and not iv_data.empty:
    plot_iv_over_time(iv_data, option_type)
else:
    print("No data to plot or data fetching failed.")
