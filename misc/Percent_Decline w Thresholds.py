import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

# Fetch historical data for ^VIX
vix_data = yf.download('^VIX', start='1990-01-01')

# Define the spike threshold and the median level
spike_threshold = 35
median_level = 17.6

# Find dates where VIX spiked above the threshold
spike_dates = vix_data[vix_data['Close'] > spike_threshold].index

# Calculate the number of trading sessions it took to return to the median level after each spike
sessions_to_median = []
for spike_date in spike_dates:
    # Find the first date after the spike where VIX closes below the median level
    post_spike_data = vix_data[spike_date:]
    below_median_date = post_spike_data[post_spike_data['Close'] < median_level].index
    if len(below_median_date) > 0:
        sessions_count = (below_median_date[0] - spike_date).days
        sessions_to_median.append((spike_date.strftime('%m/%d/%Y'), sessions_count))

# Sort the results by the number of sessions
sessions_to_median.sort(key=lambda x: x[1], reverse=True)

# Separate the dates and session counts for plotting
spike_dates_formatted, sessions_counts = zip(*sessions_to_median)

# Calculate the average number of sessions
average_sessions = np.mean(sessions_counts)

# Create the bar chart
plt.figure(figsize=(14, 8))
plt.bar(spike_dates_formatted, sessions_counts, color='orange', label='Trading Sessions to Return Below 17.6')
plt.axhline(average_sessions, color='blue', linestyle='--', label=f'Average: {average_sessions:.2f} Sessions')

# Adding titles and labels
plt.title('History of VIX Spikes', fontsize=16)
plt.xlabel('Spike Date', fontsize=12)
plt.ylabel('No. of Trading Sessions to Return Below 17.6 after Close > 35', fontsize=12)
plt.xticks(rotation=45, ha='right')

# Adding watermark to the background
plt.text(0.5, 0.5, '@o5341V', fontsize=100, color='gray', alpha=0.3,
         ha='center', va='center', rotation=30, transform=plt.gcf().transFigure)

# Show the legend
plt.legend()

# Show the plot
plt.tight_layout()
plt.show()
