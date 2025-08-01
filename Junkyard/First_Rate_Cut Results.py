import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

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

# Calculate returns after rate cuts
returns = {"Date": [], "3 Months": [], "6 Months": [], "12 Months": []}

def get_nearest_trading_day(date, spx):
    """Get the nearest trading day for a given date."""
    while date not in spx.index:
        date += timedelta(days=1)
    return date

for cut_date in rate_cut_dates:
    returns["Date"].append(cut_date)
    for period in ["3 Months", "6 Months", "12 Months"]:
        end_date = cut_date + timedelta(days=90 if period == "3 Months" else 180 if period == "6 Months" else 365)
        end_date = get_nearest_trading_day(end_date, spx)
        if end_date in spx.index:
            start_price = spx.loc[cut_date, "Adj Close"]
            end_price = spx.loc[end_date, "Adj Close"]
            returns[period].append((end_price - start_price) / start_price)
        else:
            returns[period].append(None)

# Create a DataFrame to display the results
results_df = pd.DataFrame(returns)

# Calculate averages
average_3_months = results_df["3 Months"].mean()
average_6_months = results_df["6 Months"].mean()
average_12_months = results_df["12 Months"].mean()

# Calculate SPX average returns for comparison
spx['Returns'] = spx['Adj Close'].pct_change()

def calculate_rolling_return(spx, days):
    return spx['Adj Close'].pct_change(periods=days).mean()

spx_avg_3_months = calculate_rolling_return(spx, 90)
spx_avg_6_months = calculate_rolling_return(spx, 180)
spx_avg_12_months = calculate_rolling_return(spx, 365)

# Format results as percentages
averages = {
    "Date": ["Average"],
    "3 Months": [f"{average_3_months * 100:.2f}% (SPX Avg: {spx_avg_3_months * 100:.2f}%)"],
    "6 Months": [f"{average_6_months * 100:.2f}% (SPX Avg: {spx_avg_6_months * 100:.2f}%)"],
    "12 Months": [f"{average_12_months * 100:.2f}% (SPX Avg: {spx_avg_12_months * 100:.2f}%)"],
}

# Append averages to the DataFrame
averages_df = pd.DataFrame(averages)
results_df = pd.concat([results_df, averages_df], ignore_index=True)

# Print the DataFrame
print(results_df)

# Save the DataFrame to a CSV file
results_df.to_csv("spx_returns_after_rate_cuts.csv", index=False)
