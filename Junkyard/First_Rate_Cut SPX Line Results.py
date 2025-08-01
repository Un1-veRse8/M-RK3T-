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
spx = yf.download("^GSPC", start="1900-01-01", end="2024-07-01")

# Convert rate cut dates to datetime
rate_cut_dates = [datetime.strptime(date, "%Y-%m-%d") for date in rate_cut_dates]

# Plot SPX performance one year before and one year after each rate cut
plt.figure(figsize=(14, 8))

for cut_date in rate_cut_dates:
    start_date = cut_date - timedelta(days=365)
    end_date = cut_date + timedelta(days=365)
    period_spx = spx[(spx.index >= start_date) & (spx.index <= end_date)]
    
    # Plot the SPX data
    plt.plot(period_spx.index, period_spx['Adj Close'], label=cut_date.strftime('%Y-%m-%d'))

# Add a vertical line to indicate the rate cut date
    plt.axvline(x=cut_date, color='r', linestyle='--')

plt.title('SPX Performance One Year Before and One Year After Fed Rate Cuts')
plt.xlabel('Date')
plt.ylabel('SPX Index Level')
plt.legend(title="Rate Cut Date")
plt.grid(True)
plt.show()
