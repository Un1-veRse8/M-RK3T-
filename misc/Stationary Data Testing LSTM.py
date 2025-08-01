import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Step 1: Fetch and preprocess data
def fetch_sp500_data():
    """
    Fetch historical S&P 500 data from Yahoo Finance.
    """
    sp500 = yf.Ticker("^GSPC")
    df = sp500.history(period="max")
    df.reset_index(inplace=True)
    df = df[['Date', 'Close']]
    df.rename(columns={'Date': 'date', 'Close': 'value'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    return df

# Fetch S&P 500 data
sp500_data = fetch_sp500_data()
sp500_data.set_index('date', inplace=True)

# Plot original data
plt.figure(figsize=(12, 6))
plt.plot(sp500_data['value'], label="S&P 500 (Original Data)", color="blue")
plt.title("S&P 500 Historical Data")
plt.xlabel("Date")
plt.ylabel("Index Value")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# Step 2: Scale data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(sp500_data['value'].values.reshape(-1, 1))

# Step 3: Create training and testing datasets
train_size = int(len(scaled_data) * 0.8)
train_data = scaled_data[:train_size]
test_data = scaled_data[train_size:]

# Function to create sequences
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(seq_length, len(data)):
        X.append(data[i-seq_length:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)

seq_length = 60  # Number of days to look back
X_train, y_train = create_sequences(train_data, seq_length)
X_test, y_test = create_sequences(test_data, seq_length)

# Reshape for LSTM input
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# Step 4: Build the LSTM model
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25),
    Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error')

# Step 5: Train the model
print("Training the LSTM model...")
model.fit(X_train, y_train, batch_size=1, epochs=5)

# Step 6: Make predictions
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)  # Rescale to original values

# Plot the predictions
plt.figure(figsize=(12, 6))
plt.plot(sp500_data.index[-len(y_test):], scaler.inverse_transform(y_test.reshape(-1, 1)), label="True Data", color="blue")
plt.plot(sp500_data.index[-len(predictions):], predictions, label="LSTM Predictions", color="orange")
plt.title("S&P 500 Forecast with LSTM")
plt.xlabel("Date")
plt.ylabel("Index Value")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# Step 7: Forecast future values
future_steps = 30  # Number of days to forecast
last_sequence = scaled_data[-seq_length:]  # Take the last sequence from the original data
future_predictions = []

for _ in range(future_steps):
    next_prediction = model.predict(last_sequence.reshape(1, seq_length, 1))[0, 0]
    future_predictions.append(next_prediction)
    last_sequence = np.append(last_sequence[1:], [[next_prediction]], axis=0)

# Rescale future predictions to original scale
future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

# Plot the future predictions
future_dates = pd.date_range(start=sp500_data.index[-1], periods=future_steps + 1, freq='B')[1:]

plt.figure(figsize=(12, 6))
plt.plot(sp500_data.index, sp500_data['value'], label="Historical Data", color="blue")
plt.plot(future_dates, future_predictions, label="LSTM Forecast", color="orange")
plt.title("S&P 500 Future Forecast with LSTM")
plt.xlabel("Date")
plt.ylabel("Index Value")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
