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

    if prev_macd < prev_signal and curr_macd > curr_signal:
        signals.append({'Datetime': dt, 'Signal': 'Buy'})
    elif prev_macd > prev_signal and curr_macd < curr_signal:
        signals.append({'Datetime': dt, 'Signal': 'Sell'})

# 🔹 Save to Excel
signals_df = pd.DataFrame(signals)
signals_df.to_excel("tcs_macd_signals.xlsx", index=False, sheet_name="Signals")

# 🔹 Plot
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(16, 8))

# MACD and Signal lines
ax.plot(df['Datetime'], df['MACD'], label='MACD Line', color='red', linewidth=2)
ax.plot(df['Datetime'], df['Signal'], label='Signal Line', color='blue', linestyle='--', linewidth=2)

# Continuous Histogram bars
delta = (df['Datetime'].iloc[1] - df['Datetime'].iloc[0]).total_seconds()
bar_width = delta / (24 * 60 * 60) * 0.98
for i in range(len(df)):
    color = 'green' if df['Histogram'].iloc[i] >= 0 else 'red'
    ax.bar(df['Datetime'].iloc[i], df['Histogram'].iloc[i],
           width=bar_width, color=color, align='center', edgecolor='black', linewidth=0.2)

# Mark crossover arrows
for signal in signals:
    dt = signal['Datetime']
    typ = signal['Signal']
    idx = df.index[df['Datetime'] == dt][0]
    y_val = df['MACD'].iloc[idx]
    color = 'green' if typ == 'Buy' else 'red'
    ax.annotate(typ,
                xy=(dt, y_val),
                xytext=(dt, y_val + (0.2 if typ == 'Buy' else -0.2)),
                arrowprops=dict(facecolor=color, shrink=0.05),
                fontsize=9, color=color, ha='center')

# Formatting
ax.set_title('MACD Indicator - TCS (1H)', fontsize=18, fontweight='bold')
ax.set_xlabel('Datetime', fontsize=12)
ax.set_ylabel('MACD Value', fontsize=12)
ax.legend(loc='upper left')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ✅ Confirm export
print("✅ Crossover signals saved to 'tcs_macd_signals.xlsx'")
