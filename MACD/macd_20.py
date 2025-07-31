import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 🔹 Step 1: Load Excel file and select 20 rows
file_path = "tcs_1h_data.xlsx"
df = pd.read_excel(file_path, sheet_name='Sheet1')

# 🔹 Step 2: Prepare Data
df['Datetime'] = pd.to_datetime(df['Datetime'])
df['Close'] = pd.to_numeric(df['Close TCS.NS'], errors='coerce')
df = df[['Datetime', 'Close']].dropna().head(20)

# 🔹 Step 3: Calculate MACD and Histogram
df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = df['EMA12'] - df['EMA26']
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['Histogram'] = df['MACD'] - df['Signal']

# 🔹 Step 4: Plot with Continuous Bar Histogram
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(16, 8))

# MACD & Signal Lines
ax.plot(df['Datetime'], df['MACD'], label='MACD Line', color='red', linewidth=2)
ax.plot(df['Datetime'], df['Signal'], label='Signal Line', color='blue', linestyle='--', linewidth=2)

# ✅ Continuous Histogram Bars (green/red) with no gaps
# Calculate time delta between bars
delta = (df['Datetime'].iloc[1] - df['Datetime'].iloc[0]).total_seconds()
width = delta / (24 * 60 * 60) * 0.99  # ~99% of time width

# Draw bullish and bearish histogram bars separately for color
for i in range(len(df)):
    color = 'green' if df['Histogram'].iloc[i] >= 0 else 'red'
    ax.bar(df['Datetime'].iloc[i], df['Histogram'].iloc[i],
           width=width, color=color, align='center', edgecolor='black', linewidth=0.3)

# 🔹 Decorations
ax.set_title('MACD Indicator - TCS (1H) [Contiguous Bar Histogram]', fontsize=18, fontweight='bold')
ax.set_xlabel('Datetime', fontsize=12)
ax.set_ylabel('MACD Value', fontsize=12)
ax.legend(loc='upper left')
ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.xticks(rotation=45)
plt.tight_layout()

# 🔹 Show
plt.show()
