import yfinance as yf
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta, date

# Interval and period options
interval_options = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
period_options = ['1d', '5d', '7d', '30d', '60d', '90d', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

def download_1h_limited_data(ticker):
    # Set end_date to today's date at midnight to avoid future date issues
    end_date = datetime.combine(date.today(), datetime.min.time())
    start_date = end_date - timedelta(days=730)  # last 2 years max allowed by Yahoo for 1h interval

    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    status_label.config(text=f"📥 Downloading {ticker} 1h data from {start_str} to {end_str} (max 2 years)...")
    root.update()

    try:
        data = yf.download(ticker, interval='1h', start=start_str, end=end_str)
        if data.empty:
            status_label.config(text="⚠️ No data found for this range.")
            return None
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [' '.join(col).strip() for col in data.columns.values]
        return data
    except Exception as e:
        messagebox.showerror("Error", f"Error downloading data:\n{e}")
        return None

def download_data(ticker, interval, period):
    ticker = ticker.upper()
    if interval in ['1h', '60m', '90m']:
        data = download_1h_limited_data(ticker)
        if data is None or data.empty:
            status_label.config(text="⚠️ No data downloaded.")
            return

        data.reset_index(inplace=True)
        datetime_col = 'Datetime' if 'Datetime' in data.columns else 'Date'
        data[datetime_col] = data[datetime_col].dt.strftime('%Y-%m-%d %H:%M:%S')

        file_name = f"{ticker.replace('.NS','').replace('.', '_').lower()}_{interval}_2yr.xlsx"
        data.to_excel(file_name, index=False)
        status_label.config(text=f"✅ 1h interval data saved to '{file_name}' (max 2 years)")

    else:
        status_label.config(text=f"📥 Downloading data for {ticker}...")
        root.update()
        try:
            data = yf.download(ticker, interval=interval, period=period)

            if data.empty:
                status_label.config(text=f"⚠️ No data found for {ticker}")
                return

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [' '.join(col).strip() for col in data.columns.values]

            data.reset_index(inplace=True)
            datetime_col = 'Datetime' if 'Datetime' in data.columns else 'Date'
            data[datetime_col] = data[datetime_col].dt.strftime('%Y-%m-%d %H:%M:%S')

            file_name = f"{ticker.replace('.NS','').replace('.', '_').lower()}_{interval}_{period}.xlsx"
            data.to_excel(file_name, index=False)

            status_label.config(text=f"✅ Data saved to '{file_name}'")

        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to download data:\n{e}")
            status_label.config(text="❌ Error occurred.")

# === GUI Setup ===

root = tk.Tk()
root.title("📈 Stock Data Downloader")
root.geometry("420x320")
root.resizable(False, False)

# Stock symbol input
tk.Label(root, text="Enter Stock Symbol (e.g. RELIANCE.NS, AAPL):").pack(pady=7)
symbol_entry = ttk.Entry(root, width=30)
symbol_entry.insert(0, "RELIANCE.NS")
symbol_entry.pack()

# Interval dropdown
tk.Label(root, text="Select Time Interval:").pack(pady=7)
interval_combo = ttk.Combobox(root, values=interval_options, state="readonly", width=28)
interval_combo.set("1h")
interval_combo.pack()

# Period dropdown
tk.Label(root, text="Select Duration Period:").pack(pady=7)
period_combo = ttk.Combobox(root, values=period_options, state="readonly", width=28)
period_combo.set("60d")
period_combo.pack()

# Status label
status_label = tk.Label(root, text="", fg="blue")
status_label.pack(pady=15)

# Download button
def start_download():
    ticker = symbol_entry.get().strip()
    interval = interval_combo.get()
    period = period_combo.get()

    if not ticker:
        messagebox.showwarning("Input Required", "Please enter a stock symbol.")
        return

    download_data(ticker, interval, period)

ttk.Button(root, text="📥 Download Data", command=start_download).pack(pady=10)

root.mainloop()
