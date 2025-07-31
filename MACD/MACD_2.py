import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 🔹 Step 1: Load Excel file
file_path = "tcs_1h_data.xlsx"  # Ensure this file is in the same directory
df = pd.read_excel(file_path, sheet_name='Sheet1')

# 🔹 Step 2: Prepare Data
df['Datetime'] = pd.to_datetime(df['Datetime'])
df['Close'] = pd.to_numeric(df['Close TCS.NS'], errors='coerce')
df = df[['Datetime', 'Close']].dropna()

# 🔹 Step 3: Calculate EMAs, MACD, Signal Line, and Histogram
df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = df['EMA12'] - df['EMA26']
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['Histogram'] = df['MACD'] - df['Signal']

# 🔹 Step 4: Plot MACD Dashboard Style Chart
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(16, 8))

# Plot MACD and Signal lines
ax.plot(df['Datetime'], df['MACD'], label='MACD Line', color='red', linewidth=2)
ax.plot(df['Datetime'], df['Signal'], label='Signal Line', color='blue', linestyle='--', linewidth=2)

# Plot Histogram bars
ax.bar(df['Datetime'], df['Histogram'], label='Histogram', color='gray', alpha=0.6, width=0.01)

# 🔹 Chart Enhancements
ax.set_title('📈 MACD Indicator - TCS (1H)', fontsize=18, fontweight='bold')
ax.set_xlabel('Datetime', fontsize=12)
ax.set_ylabel('MACD Value', fontsize=12)
ax.legend(loc='upper left')
ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.xticks(rotation=45)
plt.tight_layout()

# 🔹 Display the plot
plt.show()
