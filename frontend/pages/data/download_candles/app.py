#Added a colapsable container with 2 buttons that would make date selection for 3 days or 7 days in the past. 
#Added a dropdown that would list current saved files. 
#Added a load and delete for this.
from datetime import datetime, timedelta, time 
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from frontend.st_utils import get_backend_api_client, initialize_st_page

# Initialize Streamlit page
initialize_st_page(title="Download Candles", icon="💾")
backend_api_client = get_backend_api_client()

# Directory to save and load data
DATA_DIR = os.path.expanduser("~home/frontend/pages/data/download_candles")
os.makedirs(DATA_DIR, exist_ok=True)

# Set default dates
today = datetime.today()
default_start_date = today - timedelta(days=7)
default_end_date = today

# Collapsible container for quick date selection
with st.expander("Quick Date Selection", expanded=False):
  col1, col2 = st.columns([1, 1])
  with col1:
      if st.button("Last 7 Days"):
          default_start_date = today - timedelta(days=7)
          default_end_date = today
  with col2:
      if st.button("Last 3 Days"):
          default_start_date = today - timedelta(days=3)
          default_end_date = today

c1, c2, c3, c4 = st.columns([2, 2, 2, 0.5])
with c1:
  connector = st.selectbox("Exchange",
                           ["binance_perpetual", "binance", "gate_io", "gate_io_perpetual", "kucoin", "ascend_ex"],
                           index=0)
  trading_pair = st.text_input("Trading Pair", value="BTC-USDT")
with c2:
  interval = st.selectbox("Interval", options=["1m", "3m", "5m", "15m", "1h", "4h", "1d", "1s"])
with c3:
  start_date = st.date_input("Start Date", value=default_start_date)
  end_date = st.date_input("End Date", value=default_end_date)
with c4:
  get_data_button = st.button("Get Candles!")

# Load saved data
saved_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

if saved_files:
  selected_file = st.selectbox("Select Saved Data", options=saved_files)

  if st.button("Load Selected Data"):
      if selected_file:
          candles_df = pd.read_csv(os.path.join(DATA_DIR, selected_file))
          candles_df.index = pd.to_datetime(candles_df["timestamp"], unit='s')

          # Plotting the candlestick chart
          fig = go.Figure(data=[go.Candlestick(
              x=candles_df.index,
              open=candles_df['open'],
              high=candles_df['high'],
              low=candles_df['low'],
              close=candles_df['close'],
              increasing_line_color='#2ECC71',
              decreasing_line_color='#E74C3C'
          )])
          fig.update_layout(
              height=1000,
              title=dict(text="Candlesticks", font=dict(size=14)),
              xaxis_title="Time",
              yaxis_title="Price",
              template="plotly_dark",
              showlegend=False
          )
          fig.update_xaxes(rangeslider_visible=False)
          fig.update_yaxes(title_text="Price")
          st.plotly_chart(fig, use_container_width=True)

  if st.button("Delete Selected Data"):
      if selected_file:
          os.remove(os.path.join(DATA_DIR, selected_file))
          st.success(f"Deleted {selected_file}")
          st.experimental_rerun()

if get_data_button:
  start_datetime = datetime.combine(start_date, time.min)
  end_datetime = datetime.combine(end_date, time.max)

  candles = backend_api_client.get_historical_candles(
      connector=connector,
      trading_pair=trading_pair,
      interval=interval,
      start_time=int(start_datetime.timestamp()),
      end_time=int(end_datetime.timestamp())
  )

  candles_df = pd.DataFrame(candles)
  candles_df.index = pd.to_datetime(candles_df["timestamp"], unit='s')

  # Plotting the candlestick chart
  fig = go.Figure(data=[go.Candlestick(
      x=candles_df.index,
      open=candles_df['open'],
      high=candles_df['high'],
      low=candles_df['low'],
      close=candles_df['close'],
      increasing_line_color='#2ECC71',
      decreasing_line_color='#E74C3C'
  )])
  fig.update_layout(
      height=1000,
      title=dict(text="Candlesticks", font=dict(size=14)),
      xaxis_title="Time",
      yaxis_title="Price",
      template="plotly_dark",
      showlegend=False
  )
  fig.update_xaxes(rangeslider_visible=False)
  fig.update_yaxes(title_text="Price")
  st.plotly_chart(fig, use_container_width=True)

  # Generating CSV and download button
  csv = candles_df.to_csv(index=False)
  filename = f"{connector}_{trading_pair}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
  
  # Save to specified directory
  file_path = os.path.join(DATA_DIR, filename)
  with open(file_path, 'w') as f:
      f.write(csv)
  
  # Save to current working directory
  with open(filename, 'w') as f:
      f.write(csv)
  
  st.download_button(
      label="Download Candles as CSV",
      data=csv,
      file_name=filename,
      mime='text/csv',
  )
