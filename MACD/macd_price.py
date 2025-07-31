import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 🔹 Load the Excel data
file_path = "tcs_1h_data.xlsx"
df = pd.read_excel(file_path, sheet_name='Sheet1')

# 🔹 Preprocess
df['Datetime'] = pd.to_datetime(df['Datetime'])
df['Close'] = pd.to_numeric(df['Close TCS.NS'], errors='coerce')
df = df[['Datetime', 'Close']].dropna().reset_index(drop=True)

# 🔹 MACD calculations
df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = df['EMA12'] - df['EMA26']
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['Histogram'] = df['MACD'] - df['Signal']

# 🔹 Detect crossover points
signals = []
for i in range(1, len(df)):
    prev_macd = df['MACD'].iloc[i - 1]
    prev_signal = df['Signal'].iloc[i - 1]
    curr_macd = df['MACD'].iloc[i]
    curr_signal = df['Signal'].iloc[i]
    dt = df['Datetime'].iloc[i]
    price = df['Close'].iloc[i]

    if prev_macd < prev_signal and curr_macd > curr_signal:
        signals.append({'Datetime': dt, 'Signal': 'Buy', 'Price': price})
    elif prev_macd > prev_signal and curr_macd < curr_signal:
        signals.append({'Datetime': dt, 'Signal': 'Sell', 'Price': price})

# 🔹 Save to Excel
signals_df = pd.DataFrame(signals)
signals_df.to_excel("tcs_macd_signals_with_price.xlsx", index=False, sheet_name="Signals")

# 🔹 Plot Price + MACD in subplots
plt.style.use('seaborn-v0_8-darkgrid')
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(16, 10), sharex=True)

# 🔸 PRICE chart
ax1.plot(df['Datetime'], df['Close'], label='Close Price', color='black')
ax1.set_title('📈 TCS Price with MACD Buy/Sell Signals', fontsize=16, fontweight='bold')
ax1.set_ylabel('Price')
for signal in signals:
    color = 'green' if signal['Signal'] == 'Buy' else 'red'
    ax1.plot(signal['Datetime'], signal['Price'], marker='^' if signal['Signal'] == 'Buy' else 'v',
             color=color, markersize=10, label=signal['Signal'])

# 🔸 MACD chart
ax2.plot(df['Datetime'], df['MACD'], label='MACD', color='red', linewidth=2)
ax2.plot(df['Datetime'], df['Signal'], label='Signal', color='blue', linestyle='--', linewidth=2)

# Histogram bars (continuous)
delta = (df['Datetime'].iloc[1] - df['Datetime'].iloc[0]).total_seconds()
bar_width = delta / (24 * 60 * 60) * 0.98
for i in range(len(df)):
    color = 'green' if df['Histogram'].iloc[i] >= 0 else 'red'
    ax2.bar(df['Datetime'].iloc[i], df['Histogram'].iloc[i],
            width=bar_width, color=color, align='center', edgecolor='black', linewidth=0.2)

ax2.set_ylabel('MACD Value')
ax2.set_xlabel('Datetime')
ax2.legend(loc='upper left')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ✅ Confirm export
print("✅ 'tcs_macd_signals_with_price.xlsx' saved with Buy/Sell signals and corresponding prices.")
