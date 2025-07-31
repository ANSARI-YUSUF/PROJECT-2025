import yfinance as yf
import pandas as pd

ticker = 'TCS.NS'

data = yf.download(ticker, interval='1h', period='2y')

# Flatten MultiIndex columns if any
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [' '.join(col).strip() for col in data.columns.values]

# Reset index to get datetime as column
data.reset_index(inplace=True)

# Convert datetime to string for Excel
data['Datetime'] = data['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Save to Excel without index
data.to_excel('tcs_1h_data.xlsx', index=False)

print("✅ Saved 1-hour TCS data to 'tcs_1h_data.xlsx'")
print(data.head())