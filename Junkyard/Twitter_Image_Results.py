import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec

# Define the periods based on the image, excluding 'A' years
periods = {
    'B': [1935, 1945, 1953, 1962, 1972, 1980, 1989, 1999, 2007, 2016, 2026, 2034, 2043, 2053],
    'C': [1931, 1942, 1951, 1958, 1969, 1978, 1985, 1996, 2005, 2012, 2023, 2032, 2039, 2050, 2059]
}

# Function to calculate returns for both strategies
def calculate_returns(return_type):
    # Fetch historical SPX data from Yahoo Finance starting from 1920
    spx = yf.download('^GSPC', start='1920-01-01')
    
    # Add signal column based on periods
    spx['Signal'] = 0
    for year in periods['B']:
        spx.loc[spx.index.year == year, 'Signal'] = -1  # B: Sell years
    for year in periods['C']:
        spx.loc[spx.index.year == year, 'Signal'] = 1  # C: Buy years

    # Backtesting the strategy based on signals
    initial_investment = 1
    cash = initial_investment
    position = 0
    portfolio_value_signal = []

    for date, row in spx.iterrows():
        if row['Signal'] == 1 and cash > 0:  # Buy signal
            position = cash / row['Close']
            cash = 0
        elif row['Signal'] == -1 and position > 0:  # Sell signal
            cash = position * row['Close']
            position = 0
        portfolio_value_signal.append(cash if cash > 0 else position * row['Close'])

    spx['Portfolio Value Signal'] = portfolio_value_signal

    if return_type == 'percent':
        # Convert portfolio values to percentage returns
        spx['Portfolio Value Signal'] = (spx['Portfolio Value Signal'] / initial_investment - 1) * 100
        # Backtesting the buy and hold strategy
        spx['Portfolio Value Buy and Hold'] = (spx['Close'] / spx['Close'].iloc[0] - 1) * 100
    else:
        # Backtesting the buy and hold strategy with dollar returns
        spx['Portfolio Value Buy and Hold'] = initial_investment * (spx['Close'] / spx['Close'].iloc[0])
    
    return spx

# Ask the user if they want percentage returns or dollar returns
return_type = input("Do you want percentage returns or dollar returns? (percent/dollar): ").strip().lower()

# Calculate returns
spx = calculate_returns(return_type)

# Define line width
line_width = 0.5  # Adjusted for better visibility

# Plotting the results
fig = plt.figure(figsize=(18, 12))
gs = GridSpec(3, 2, height_ratios=[1, 1, 1])

# Plot SPX Close Price
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(spx.index, spx['Close'], label='SPX Close Price', color='blue', linewidth=line_width)
for year in periods['C']:
    ax1.axvline(pd.Timestamp(str(year)), color='g', linestyle='-', linewidth=line_width, label='Buy Year' if year == periods['C'][0] else "")
    ax1.text(pd.Timestamp(str(year)), spx['Close'].min(), str(year), color='black', rotation=90, verticalalignment='bottom', horizontalalignment='center')
for year in periods['B']:
    ax1.axvline(pd.Timestamp(str(year)), color='r', linestyle='-', linewidth=line_width, label='Sell Year' if year == periods['B'][0] else "")
    ax1.text(pd.Timestamp(str(year)), spx['Close'].max(), str(year), color='black', rotation=90, verticalalignment='top', horizontalalignment='center')
ax1.set_title('SPX Historical Prices with Buy/Sell Years (Logarithmic Scale)')
ax1.set_ylabel('SPX Price')
ax1.set_yscale('log')
ax1.legend()
ax1.grid(False)

# Plot Portfolio Value (Signal Strategy)
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(spx.index, spx['Portfolio Value Signal'], label='Portfolio Value (Signal Strategy)', linestyle='--', color='green', linewidth=line_width)
if return_type == 'percent':
    ax2.set_ylabel('Portfolio Value (Signal Strategy) (%)')
else:
    ax2.set_ylabel('Portfolio Value (Signal Strategy) ($)')
ax2.legend(loc='upper left')
ax2.grid()

# Plot Portfolio Value (Buy and Hold)
ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(spx.index, spx['Portfolio Value Buy and Hold'], label='Portfolio Value (Buy and Hold)', linestyle='-.', color='red', linewidth=line_width)
if return_type == 'percent':
    ax3.set_ylabel('Portfolio Value (Buy and Hold) (%)')
else:
    ax3.set_ylabel('Portfolio Value (Buy and Hold) ($)')
ax3.legend(loc='upper left')
ax3.grid()
ax3.get_yaxis().get_major_formatter().set_scientific(False)

# Add watermark
fig.text(0.5, 0.5, 'o5341V', fontsize=50, color='gray', ha='center', va='center', alpha=0.5, rotation=45)

fig.suptitle(f'Portfolio Value Comparison ({return_type.capitalize()} Returns)\nInitial Investment of $1', fontsize=16)
plt.xlabel('Date')
plt.show()
