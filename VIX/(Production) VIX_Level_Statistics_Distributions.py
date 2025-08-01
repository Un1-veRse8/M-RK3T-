import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
import tkinter as tk
from datetime import datetime
from scipy import stats

# Set the start date to the earliest available data
start_date = "1900-01-01"  # Setting an early date to get the maximum range
end_date = datetime.today().strftime('%Y-%m-%d')

# Fetch historical VIX data
symbol = "^VIX"
data = yf.download(symbol, start=start_date, end=end_date)

# Ensure that the data includes the most recent close
if not data.empty:
    vix_values = data['Adj Close']
else:
    print("No data found for the specified date range.")
    exit()

# Check if today's data is included
if end_date not in vix_values.index:
    fetch_recent = input("The most recent close is not included. Would you like to fetch the latest close automatically or manually enter it? (auto/manual): ").strip().lower()
    if fetch_recent == 'auto':
        try:
            today_data = yf.download(symbol, start=end_date, end=end_date)
            if not today_data.empty:
                most_recent_close = today_data['Adj Close'].iloc[-1]
            else:
                most_recent_close = vix_values.iloc[-1]
                print("Failed to fetch today's data automatically. Using the last available close.")
        except Exception as e:
            print(f"Error fetching today's data: {e}")
            most_recent_close = vix_values.iloc[-1]
            print("Using the last available close.")
    elif fetch_recent == 'manual':
        most_recent_close = float(input("Please enter the most recent close value: ").strip())
    else:
        most_recent_close = vix_values.iloc[-1]
        print("Invalid option. Using the last available close.")
else:
    most_recent_close = vix_values.iloc[-1]

# Append the manually entered most recent close if needed
if fetch_recent == 'manual':
    vix_values = pd.concat([vix_values, pd.Series([most_recent_close], index=[pd.Timestamp(end_date)])])

# Calculate distribution statistics
mean_vix = np.mean(vix_values)
median_vix = np.median(vix_values)
mode_vix_result = stats.mode(vix_values)
mode_vix = mode_vix_result.mode[0] if isinstance(mode_vix_result.mode, np.ndarray) and mode_vix_result.mode.size > 0 else mode_vix_result.mode
std_vix = np.std(vix_values)
total_days = len(vix_values)

# Get the minimum VIX value
min_vix = vix_values.min()

# Ask user if they want to set a ceiling for the x-axis
set_ceiling = input("Do you want to set a ceiling(cap VIX data) for the x-axis? (yes/no): ").strip().lower()
if set_ceiling == 'yes':
    max_vix = float(input("Enter the ceiling value for the x-axis (e.g., 50 for clean axis): "))
else:
    max_vix = vix_values.max()

# Ask user for the threshold value for statistics
threshold_value = float(input("Enter the threshold value for statistics (e.g., 12): "))

# Calculate above and below threshold statistics
above_threshold = vix_values[vix_values > threshold_value].count()
below_threshold = vix_values[vix_values <= threshold_value].count()
percentage_above = (above_threshold / total_days) * 100
percentage_below = (below_threshold / total_days) * 100

# Combine values above the ceiling into the ceiling bin
if set_ceiling == 'yes':
    vix_values_capped = vix_values.copy()
    vix_values_capped[vix_values_capped > max_vix] = max_vix
else:
    vix_values_capped = vix_values

# Center the plot window on the screen using tkinter
def center_window(width=800, height=600):
    root = tk.Tk()
    root.withdraw()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.destroy()
    return x, y, width, height

# Set the desired plot window size
plot_width = 1200
plot_height = 600

# Get the centered window position
x, y, width, height = center_window(plot_width, plot_height)

# Plot the VIX distribution
plt.figure(figsize=(16, 8))

# Define the minimum bin value explicitly
min_bin_value = min(min_vix, 8)

# Create bins, with a single bin for all values above max_vix if a ceiling is set
bins = np.arange(min_bin_value, max_vix + 2, 1)

# Plot histogram
n, bins, patches = plt.hist(vix_values_capped, bins=bins, color='blue', alpha=0.7, edgecolor='black')

# Highlight the bin where the most recent close falls
bin_index = np.digitize([most_recent_close], bins) - 1
bin_index = bin_index[0] if bin_index.size > 0 else -1
if 0 <= bin_index < len(patches):
    patches[bin_index].set_facecolor('yellow')

# Add line for the most recent close
line1 = plt.axvline(most_recent_close, color='red', linestyle='solid', linewidth=1, label='Most Recent Close')

# Add line for the threshold value
line2 = plt.axvline(threshold_value, color='red', linestyle='dotted', linewidth=1, label='Threshold Value')


# Add text box for statistics
stats_text = f"""Most Recent Close: {most_recent_close:.2f}
Mean: {mean_vix:.2f}
Median: {median_vix:.2f}
Mode: {mode_vix:.2f}
Std Dev: {std_vix:.2f}
Total Days(Bar Count): {total_days}
Above {threshold_value}: {above_threshold} ({percentage_above:.2f}%)
Below or equal {threshold_value}: {below_threshold} ({percentage_below:.2f}%)"""

plt.text(0.95, 0.95, stats_text, transform=plt.gca().transAxes, fontsize=12,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(facecolor='white', alpha=0.6))

# Adding a text watermark
plt.text(0.5, 0.5, 'o5341V', fontsize=70, color='gray', ha='center', va='center', alpha=0.1, transform=plt.gca().transAxes)

# Adding a more transparent watermark behind the stats
plt.text(0.98, 0.89, 'o5341V', fontsize=70, color='gray', ha='right', va='top', alpha=0.1, transform=plt.gca().transAxes)

plt.title('VIX Distribution')
plt.xlabel('VIX Value')
plt.ylabel('Frequency')

# Customize x-axis ticks
ax = plt.gca()
ax.set_xlim(left=min_bin_value, right=max_vix + 1)  # Set the limits to the minimum bin value and the focused maximum if ceiling is set
ax.xaxis.set_major_locator(MultipleLocator(1))
ax.xaxis.set_minor_locator(MultipleLocator(0.5))

# Add custom x-axis tick for the ceiling with a "+" sign
if set_ceiling == 'yes':
    ticks = list(np.arange(min_bin_value, max_vix + 1, 1))
    ticks.append(max_vix + 0.5)
    ax.set_xticks(ticks)
    labels = [item.get_text() for item in ax.get_xticklabels()]
    labels[-1] = f'{int(max_vix)}+'
    ax.set_xticklabels(labels)

# Adjust plot margins to avoid overlap and reduce whitespace
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15)

plt.grid(False)

# Add legend
plt.legend(handles=[line1, line2], loc='upper center')

# Create the plot window and set its position
manager = plt.get_current_fig_manager()
manager.window.wm_geometry(f"{width}x{height}+{x}+{y}")

plt.show()
