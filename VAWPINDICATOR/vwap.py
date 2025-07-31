import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import ticker

# Fetch AAPL data and calculate VWAP
def get_aapl_data():
    aapl = yf.Ticker("AAPL")
    data = aapl.history(period="60d", interval="15m")
    
    # Calculate VWAP: (Typical Price * Volume) / Cumulative Volume
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    data['VWAP'] = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
    
    return data

# Detect VWAP crossovers and return signals
def detect_crossovers(data):
    signals = []
    for i in range(1, len(data)):
        prev_close = data['Close'].iloc[i-1]
        prev_vwap = data['VWAP'].iloc[i-1]
        curr_close = data['Close'].iloc[i]
        curr_vwap = data['VWAP'].iloc[i]
        
        if prev_close > prev_vwap and curr_close < curr_vwap:
            signals.append((data.index[i], 'Down', data['Close'].iloc[i]))
        elif prev_close < prev_vwap and curr_close > curr_vwap:
            signals.append((data.index[i], 'Up', data['Close'].iloc[i]))
    
    return signals

def plot_data(data, signals):
    # Create figure with dark background
    plt.figure(figsize=(16, 10), facecolor='#1a1a1a')
    ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5)
    ax2 = plt.subplot2grid((6, 1), (5, 0), sharex=ax1)
    
    # Set background colors
    for ax in [ax1, ax2]:
        ax.set_facecolor('#1a1a1a')
        ax.tick_params(axis='both', colors='white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
    
    # Main Price and VWAP Plot
    ax1.plot(data.index, data['Close'], label='AAPL Price', 
            color='#4dff4d', linewidth=2, alpha=0.9)
    ax1.plot(data.index, data['VWAP'], label='VWAP', 
            color='#ff6666', linestyle='--', linewidth=2, alpha=0.9)
    
    # Highlight crossovers
    for date, signal, price in signals:
        if signal == 'Up':
            ax1.scatter(date, price, color='#00cc00', marker='^', s=150, 
                       edgecolor='white', linewidth=1, zorder=5)
            ax1.annotate('BUY', (date, price),
                        textcoords="offset points", xytext=(0,15),
                        ha='center', fontsize=10, weight='bold', color='white',
                        bbox=dict(boxstyle='round,pad=0.3', fc='green', alpha=0.8))
        else:
            ax1.scatter(date, price, color='#ff3333', marker='v', s=150,
                       edgecolor='white', linewidth=1, zorder=5)
            ax1.annotate('SELL', (date, price),
                        textcoords="offset points", xytext=(0,-20),
                        ha='center', fontsize=10, weight='bold', color='white',
                        bbox=dict(boxstyle='round,pad=0.3', fc='red', alpha=0.8))
    
    # Volume Plot
    ax2.bar(data.index, data['Volume'], color='#3399ff', alpha=0.6, width=0.02)
    
    # Formatting
    ax1.set_title('AAPL 15min Price vs VWAP with Trading Signals (Last 60 Days)', 
                 fontsize=14, pad=20, weight='bold', color='white')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.legend(loc='upper left', fontsize=10, facecolor='#1a1a1a', edgecolor='white')
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.2f}'))
    
    # Date formatting
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax2.set_ylabel('Volume', fontsize=10)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Get data and detect signals
    aapl_data = get_aapl_data()
    crossovers = detect_crossovers(aapl_data)
    
    # Print summary
    print(f"Found {len(crossovers)} VWAP crossovers in last 60 days")
    if crossovers:
        last_signal = crossovers[-1]
        print(f"Last signal: {last_signal[0]} ({last_signal[1]}) at ${last_signal[2]:.2f}")
    
    # Plot the chart
    plot_data(aapl_data, crossovers)