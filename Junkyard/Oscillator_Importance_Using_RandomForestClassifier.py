import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Fetch historical data
data = yf.download('^GSPC', start='1980-01-01', end=None)
data['Returns'] = data['Close'].pct_change()

# Calculate RSI
def calculate_rsi(series, period=14):
    delta = series.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

data['RSI'] = calculate_rsi(data['Close'])

# Calculate additional features
data['MACD'] = data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()
data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
data['Stochastic'] = ((data['Close'] - data['Low'].rolling(window=14).min()) / 
                      (data['High'].rolling(window=14).max() - data['Low'].rolling(window=14).min())) * 100
data['ATR'] = data['High'].rolling(window=14).max() - data['Low'].rolling(window=14).min()
data['ADX'] = data['Close'].diff().abs().rolling(window=14).mean()

# Calculate RVGI
def rvgi(data, period=14):
    close, high, low = data['Close'], data['High'], data['Low']
    v = (close - low) - (high - close)
    sv = v.rolling(window=period).sum()
    rv = (close - low).rolling(window=period).sum()
    rvgi = sv / rv
    return rvgi

data['RVGI'] = rvgi(data)

# Calculate Fisher Transform
def fisher_transform(series, period=14):
    value = (2 * ((series - series.min()) / (series.max() - series.min())) - 1).rolling(window=period).mean()
    fisher = 0.5 * np.log((1 + value) / (1 - value))
    return fisher

data['Fisher'] = fisher_transform(data['Close'])

# Create the target variable: 1 if the next day's return is positive, 0 otherwise
data['Target'] = (data['Returns'].shift(-1) > 0).astype(int)

# Drop NaN values
data = data.dropna()

# Select features and target
features = ['RSI', 'MACD', 'Signal_Line', 'Stochastic', 'ATR', 'ADX', 'RVGI', 'Fisher']
target = 'Target'

X = data[features]
y = data[target]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Grid search to find the best n_estimators
param_grid = {'n_estimators': [50, 100, 200, 500]}
grid_search = GridSearchCV(estimator=RandomForestClassifier(random_state=42), param_grid=param_grid, cv=5)
grid_search.fit(X_train, y_train)

# Get the best number of trees
best_n_estimators = grid_search.best_params_['n_estimators']
print(f"Best n_estimators: {best_n_estimators}")

# Train a RandomForestClassifier with the best n_estimators
model = RandomForestClassifier(n_estimators=best_n_estimators, random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
classification_report_text = classification_report(y_test, y_pred)
print(classification_report_text)

# Plot feature importance
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]
plt.figure(figsize=(10, 6))
plt.title('Feature Importances')
plt.bar(range(X.shape[1]), importances[indices], align='center')
plt.xticks(range(X.shape[1]), [features[i] for i in indices])
plt.ylabel('Importance Score')
plt.tight_layout()
plt.show()

# Remove the two least important features
least_important_features = [features[i] for i in indices[-2:]]
print(f'Removing least important features: {least_important_features}')

X = X.drop(columns=least_important_features)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Retrain the model
model = RandomForestClassifier(n_estimators=best_n_estimators, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Evaluate the model again
classification_report_text = classification_report(y_test, y_pred)
print(classification_report_text)

# Plot feature importance again
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]
plt.figure(figsize=(10, 6))
plt.title('Feature Importances After Removal')
plt.bar(range(X.shape[1]), importances[indices], align='center')
plt.xticks(range(X.shape[1]), [X.columns[i] for i in indices])
plt.ylabel('Importance Score')
plt.tight_layout()
plt.show()

# Explanation of classification report metrics
explanation = """
The rows labeled '0' and '1' in the classification report represent the performance metrics for each class in your binary classification problem.

- **Class 0**: This represents the metrics for predicting the class '0', which corresponds to days where the next day's return is not positive.
- **Class 1**: This represents the metrics for predicting the class '1', which corresponds to days where the next day's return is positive.

### Understanding the Metrics

Each row provides the following metrics:

1. **Precision**: The ratio of correctly predicted positive observations to the total predicted positives.
   - **Class 0**: Precision is the proportion of days predicted as having non-positive returns that actually had non-positive returns.
   - **Class 1**: Precision is the proportion of days predicted as having positive returns that actually had positive returns.

2. **Recall**: The ratio of correctly predicted positive observations to all observations in the actual class.
   - **Class 0**: Recall is the proportion of actual non-positive return days that were correctly identified.
   - **Class 1**: Recall is the proportion of actual positive return days that were correctly identified.

3. **F1-Score**: The weighted average of Precision and Recall, providing a balance between the two.
   - **Class 0**: F1-Score combines precision and recall for class '0' into a single metric.
   - **Class 1**: F1-Score combines precision and recall for class '1' into a single metric.

4. **Support**: The number of actual occurrences of the class in the test set.
   - **Class 0**: The number of instances of class '0' in the test set.
   - **Class 1**: The number of instances of class '1' in the test set.

### Summary Metrics

Additionally, the classification report includes summary metrics:

- **Accuracy**: The overall accuracy of the model, which is the ratio of correctly predicted instances to the total instances.
- **Macro Average**: The average of the precision, recall, and F1-score of the two classes, treating all classes equally.
- **Weighted Average**: The average of the precision, recall, and F1-score of the two classes, weighted by the number of true instances for each class.
"""

#print(explanation)
