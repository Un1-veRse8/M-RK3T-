import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def fetch_all_iv_data(symbol):
    tk = yf.Ticker(symbol)
    exps = tk.options
    if not exps:
        print("No options data available.")
        return None

    all_data = []
    for exp in exps:
        opts = tk.option_chain(exp)
        data = pd.concat([opts.calls, opts.puts])
        data['IV'] = data['impliedVolatility'] * 100  # Convert to percentage
        data['expirationDate'] = exp  # Add expiration date to DataFrame
        all_data.append(data)

    return pd.concat(all_data)

def plot_all_iv_profiles(data):
    plt.figure(figsize=(15, 8))

    # Aggregate plotting by type (Calls and Puts)
    call_data = data[data['contractSymbol'].str.contains('C')]
    put_data = data[data['contractSymbol'].str.contains('P')]

    # Debug output to check data presence
    print("Number of calls data points:", len(call_data))
    print("Number of puts data points:", len(put_data))

    # Plot if data is not empty
    if not call_data.empty:
        plt.plot(call_data['strike'], call_data['IV'], label='Calls', marker='o', linestyle='None', color='blue')
    else:
        print("No call options data available.")

    if not put_data.empty:
        plt.plot(put_data['strike'], put_data['IV'], label='Puts', marker='o', linestyle='None', color='orange')
    else:
        print("No put options data available.")

    plt.title('Implied Volatility Profile Across All Expirations')
    plt.xlabel('Strike Price')
    plt.ylabel('Implied Volatility (%)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Main execution
symbol = input("Enter the stock symbol: ")
all_data = fetch_all_iv_data(symbol)
if all_data is not None:
    plot_all_iv_profiles(all_data)
else:
    print("No options data available for plotting.")
