import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Extended dates of the first Fed rate cuts
rate_cut_dates = [
    "1987-10-20",
    "1989-07-06",
    "1991-07-02",
    "1995-07-06",
    "1998-09-29",
    "2001-01-03",
    "2007-09-18",
    "2008-12-16",
    "2019-07-31",
    "2020-03-03",
]

# Fetch all available SPX historical data
spx = yf.download("^GSPC", start="1900-01-01", end=datetime.now().strftime("%Y-%m-%d"))

# Convert rate cut dates to datetime
rate_cut_dates = [datetime.strptime(date, "%Y-%m-%d") for date in rate_cut_dates]

# Add current date to rate cut dates for the current cycle
current_date = datetime.now()
rate_cut_dates.append(current_date)

# Initialize a DataFrame to store percentage changes for averaging
days_range = range(-365, 366)
all_changes = pd.DataFrame(index=days_range)

# Plot SPX percentage change one year before and one year after each rate cut
plt.figure(figsize=(14, 8))

for cut_date in rate_cut_dates:
    start_date = cut_date - timedelta(days=365)
    end_date = cut_date + timedelta(days=365) if cut_date != current_date else cut_date
    period_spx = spx[(spx.index >= start_date) & (spx.index <= end_date)].copy()

    # Calculate percentage change from the rate cut date
    base_value = period_spx.loc[cut_date, 'Adj Close'] if cut_date in period_spx.index else period_spx.iloc[-1]['Adj Close']
    period_spx['Percentage Change'] = ((period_spx['Adj Close'] / base_value) - 1) * 100
    
    # Calculate days from rate cut
    period_spx['Days from Cut'] = (period_spx.index - cut_date).days
    
    # Reindex to ensure alignment and add to average calculation
    changes = period_spx.set_index('Days from Cut')['Percentage Change'].reindex(days_range).interpolate()
    all_changes[cut_date.strftime('%Y-%m-%d')] = changes

    # Plot the percentage change
    if cut_date == current_date:
        plt.plot(period_spx['Days from Cut'], period_spx['Percentage Change'], label='Current Cycle', linestyle='--', color='black')
    else:
        plt.plot(period_spx['Days from Cut'], period_spx['Percentage Change'], label=cut_date.strftime('%Y-%m-%d'))

# Calculate and plot the average line
average_line = all_changes.mean(axis=1)
plt.plot(average_line.index, average_line, label='Average', linestyle='-', linewidth=2, color='blue')

# Add a vertical line to indicate the rate cut date
plt.axvline(x=0, color='r', linestyle='--')

plt.title('SPX % Change One Year Before and After Fed Rate Cuts')
plt.xlabel('Days from Rate Cut')
plt.ylabel('% Change from Rate Cut Date')
plt.legend(title="Rate Cut Date")
plt.grid(True)
plt.show()
