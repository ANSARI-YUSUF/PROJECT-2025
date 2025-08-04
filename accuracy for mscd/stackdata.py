import yfinance as yf
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import os

# Settings: change ticker and date here
ticker = "AAPL"
date = "2024-07-01"

# Download 1-hour interval stock data for the day
data = yf.download(
    ticker,
    start=date,
    end=pd.to_datetime(date) + pd.Timedelta(days=1),
    interval="1h"
)

# Remove timezone info to avoid Excel issues
data.index = data.index.tz_localize(None)

# Calculate MACD components
ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
data['MACD'] = ema_12 - ema_26
data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
data['MACD_Histogram'] = data['MACD'] - data['Signal_Line']

# Previous MACD and Signal to detect crossovers
data['Prev_MACD'] = data['MACD'].shift(1)
data['Prev_Signal'] = data['Signal_Line'].shift(1)

# Initialize Performance signals as 'Hold'
data['Performance'] = 'Hold'

# Buy signal: MACD crosses above Signal line
buy_signals = (data['Prev_MACD'] < data['Prev_Signal']) & (data['MACD'] > data['Signal_Line'])

# Sell signal: MACD crosses below Signal line
sell_signals = (data['Prev_MACD'] > data['Prev_Signal']) & (data['MACD'] < data['Signal_Line'])

# Assign signals
data.loc[buy_signals, 'Performance'] = 'Buy'
data.loc[sell_signals, 'Performance'] = 'Sell'

# Drop helper columns for clarity
data = data.drop(columns=['Prev_MACD', 'Prev_Signal'])

# Create target column: next hour's performance (shift up by 1)
data['Target'] = data['Performance'].shift(-1)

# Drop last row with NaN target
data = data.dropna(subset=['Target'])

# Encode target labels to numbers
le = LabelEncoder()
data['Target_encoded'] = le.fit_transform(data['Target'])

# Features to train on
features = ['MACD', 'Signal_Line', 'MACD_Histogram']

X = data[features]
y = data['Target_encoded']

# Split into train/test (keep time order by shuffle=False)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

# Train Random Forest classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict on test set
y_pred = model.predict(X_test)

# Print classification report with label names
print(classification_report(y_test, y_pred, target_names=le.classes_))

# Save full data with signals and target to Excel
output_filename = f"{ticker}_{date}_1h_MACD_performance_with_target.xlsx"

# Check if file open
if os.path.exists(output_filename):
    try:
        with open(output_filename, 'a'):
            pass
    except PermissionError:
        print(f"ERROR: Please close '{output_filename}' before running this script.")
        exit(1)

data.to_excel(output_filename)

print(f"\nData with MACD indicators, signals, and targets saved to '{output_filename}'")


correct = 0
total = len(data) - 1  # last row has no next price

for i in range(total):
    signal = data['Performance'][i]  # Buy/Sell/Hold
    price_change = data['Close'][i+1] - data['Close'][i]

    if signal == 'Buy' and price_change > 0:
        correct += 1
    elif signal == 'Sell' and price_change < 0:
        correct += 1
    elif signal == 'Hold' and abs(price_change) <= tolerance:
        correct += 1

accuracy = (correct / total) * 100
print(f"MACD Signal Accuracy: {accuracy:.2f}%")
