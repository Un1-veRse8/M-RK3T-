import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import tkinter as tk
import matplotlib.dates as mdates

def get_user_input(prompt, default=None, input_type=str):
    while True:
        try:
            user_input = input(prompt)
            if not user_input and default is not None:
                return default
            return input_type(user_input)
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")

# Step 1: Get user input for the ticker symbol
ticker = get_user_input("Enter the ticker symbol (e.g., ^GSPC for S&P 500): ", default="^GSPC")

# Step 2: Get user input for the start year
start_year = get_user_input("Enter the start year (e.g., 2015): ", input_type=int)
start_date = f"{start_year}-01-01"

# Step 3: Get user input for the end year or use the latest available date
end_date = datetime.today().strftime('%Y-%m-%d')

# Step 4: Fetch historical data for the given ticker
data = yf.download(ticker, start=start_date, end=end_date)

# Step 5: Calculate the daily percentage change
data['Daily Change %'] = data['Adj Close'].pct_change() * 100

# Step 6: Get user input for the percentage change threshold
threshold = get_user_input("Enter the daily percentage change threshold (e.g., -2 for -2%): ", input_type=float)

# Step 7: Identify the streaks without the specified daily move
streaks = []
current_streak = 0

for change in data['Daily Change %']:
    if change >= threshold:
        current_streak += 1
    else:
        if current_streak > 0:
            streaks.append(current_streak)
        current_streak = 0

if current_streak > 0:
    streaks.append(current_streak)

# Step 8: Prepare data for plotting
streaks_dates = []
streaks_lengths = []
current_streak = 0

for i, change in enumerate(data['Daily Change %']):
    if change >= threshold:
        current_streak += 1
    else:
        if current_streak > 0:
            streaks_dates.append(data.index[i])
            streaks_lengths.append(current_streak)
        current_streak = 0

if current_streak > 0:
    streaks_dates.append(data.index[-1])
    streaks_lengths.append(current_streak)

# Step 9: Plot the streak lengths over time with enhancements

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

plt.figure(figsize=(14, 8))  # Increased the figure width to prevent overlapping
plt.plot(streaks_dates, streaks_lengths, linewidth=1, marker='o')

# Add annotations for streaks above a certain threshold
annotation_threshold = get_user_input("Enter the annotation threshold for streak lengths (e.g., 252): ", input_type=int)
for date, length in zip(streaks_dates, streaks_lengths):
    if length >= annotation_threshold:
        plt.annotate(f"{length}", (date, length), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, color='red')


# Rotate and align the date labels
plt.gcf().autofmt_xdate(rotation=45, ha='right')  # Adjusted the alignment

# Add title and labels
plt.title(f"{ticker} Streaks Without {threshold}% Daily Move", fontsize=16)
plt.xlabel("Date", fontsize=14)
plt.ylabel("Streak Length", fontsize=14)

# Adding a text watermark
plt.text(0.5, 0.5, 'o5341V', fontsize=70, color='gray', ha='center', va='center', alpha=0.1, transform=plt.gca().transAxes)

# Adding a more transparent watermark behind the stats
plt.text(0.95, 0.90, 'o5341V', fontsize=70, color='gray', ha='right', va='top', alpha=0.1, transform=plt.gca().transAxes)

# Adding a more transparent watermark behind the stats
plt.text(0.05, 0.10, 'o5341V', fontsize=70, color='gray', ha='left', va='bottom', alpha=0.1, transform=plt.gca().transAxes)

# Adjust grid lines transparency
plt.grid(True, alpha=0.5)  # Set the transparency to 50%

manager = plt.get_current_fig_manager()
manager.window.wm_geometry(f"{width}x{height}+{x}+{y}")

plt.show()
