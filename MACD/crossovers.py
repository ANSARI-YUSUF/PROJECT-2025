import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 🔹 Load the Excel File (20 rows only)
file_path = "tcs_1h_data.xlsx"
df = pd.read_excel(file_path, sheet_name='Sheet1')
df['Datetime'] = pd.to_datetime(df['Datetime'])
df['Close'] = pd.to_numeric(df['Close TCS.NS'], errors='coerce')
df = df[['Datetime', 'Close']].dropna().head(20)

# 🔹 Calculate EMAs, MACD, Signal, Histogram
df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = df['EMA12'] - df['EMA26']
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['Histogram'] = df['MACD'] - df['Signal']

# 🔹 Detect Crossover Signals
signals = []
for i in range(1, len(df)):
    prev_macd = df['MACD'].iloc[i - 1]
    prev_signal = df['Signal'].iloc[i - 1]
    curr_macd = df['MACD'].iloc[i]
    curr_signal = df['Signal'].iloc[i]
    dt = df['Datetime'].iloc[i]

    if prev_macd < prev_signal and curr_macd > curr_signal:
        signals.append((dt, 'Buy'))  # Bullish crossover
    elif prev_macd > prev_signal and curr_macd < curr_signal:
        signals.append((dt, 'Sell'))  # Bearish crossover

# 🔹 Plot MACD Chart
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(16, 8))

# MACD & Signal Lines
ax.plot(df['Datetime'], df['MACD'], label='MACD Line', color='red', linewidth=2)
ax.plot(df['Datetime'], df['Signal'], label='Signal Line', color='blue', linestyle='--', linewidth=2)

# Continuous histogram using bar chart (with no gaps)
delta = (df['Datetime'].iloc[1] - df['Datetime'].iloc[0]).total_seconds()
bar_width = delta / (24 * 60 * 60) * 0.98  # ~98% of width
for i in range(len(df)):
    color = 'green' if df['Histogram'].iloc[i] >= 0 else 'red'
    ax.bar(df['Datetime'].iloc[i], df['Histogram'].iloc[i],
           width=bar_width, color=color, align='center', edgecolor='black', linewidth=0.2)

# 🔹 Add arrows for crossover signals
for dt, signal_type in signals:
    idx = df.index[df['Datetime'] == dt][0]
    y_val = df['MACD'].iloc[idx]
    color = 'green' if signal_type == 'Buy' else 'red'
    ax.annotate(signal_type,
                xy=(dt, y_val),
                xytext=(dt, y_val + (0.2 if signal_type == 'Buy' else -0.2)),
                arrowprops=dict(facecolor=color, shrink=0.05),
                fontsize=10, color=color, ha='center')

# 🔹 Format the Chart
ax.set_title('MACD Indicator - TCS (1H) with Crossover Signals', fontsize=18, fontweight='bold')
ax.set_xlabel('Datetime', fontsize=12)
ax.set_ylabel('MACD Value', fontsize=12)
ax.legend(loc='upper left')
ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
plt.xticks(rotation=45)
plt.tight_layout()

# 🔹 Show the chart
plt.show()

# 🔹 Print crossover moments
print("📍 MACD Crossover Signals:")
for dt, typ in signals:
    print(f"{dt} --> {typ} Crossover")
