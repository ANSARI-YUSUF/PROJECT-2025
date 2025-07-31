import matplotlib.pyplot as plt
import pandas as pd

# 🔸 Step 1: Sample static closing prices (TCS-like example for 30 days)
data = {
    'Date': pd.date_range(start='2024-06-01', periods=30, freq='D'),
    'Close': [
        3750, 3745, 3752, 3760, 3775, 3782, 3770, 3765, 3750, 3748,
        3760, 3772, 3780, 3788, 3795, 3802, 3810, 3820, 3815, 3805,
        3812, 3825, 3835, 3840, 3832, 3820, 3818, 3822, 3830, 3845
    ]
}

# 🔸 Step 2: Create a DataFrame
df = pd.DataFrame(data)

# 🔸 Step 3: Calculate EMAs
df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()

# 🔸 Step 4: Calculate MACD and Signal Line
df['MACD'] = df['EMA12'] - df['EMA26']
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

# 🔸 Step 5: Calculate Histogram
df['Histogram'] = df['MACD'] - df['Signal']

# 🔸 Step 6: Plot the MACD Chart
plt.figure(figsize=(14, 7))
plt.plot(df['Date'], df['MACD'], label='MACD Line (EMA12 - EMA26)', color='blue', linewidth=2)
plt.plot(df['Date'], df['Signal'], label='Signal Line (9-day EMA of MACD)', color='orange', linestyle='--')
plt.bar(df['Date'], df['Histogram'], label='Histogram (MACD - Signal)', color='gray', alpha=0.5)

# Chart Decorations
plt.title('MACD Indicator (Static Data)')
plt.xlabel('Date')
plt.ylabel('MACD Value')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()

# 🔸 Step 7: Show the plot
plt.show()
