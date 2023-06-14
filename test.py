import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta
import vectorbt as vbt
from vectorbt.utils.decorators import cached_property
from vectorbt.portfolio.enums import SizeType
from streamlit_option_menu import option_menu
import plotly.graph_objects as go


##############
st.set_page_config(page_title="Vectorbt Example App",page_icon="🧊",layout="wide",initial_sidebar_state="expanded",
menu_items={'About': ". This is an *extremely* cool app!"})


selected2 = option_menu(None, ["Home", "candel", "RSI", 'Ema Crossover'], 
    icons=['house', 'rocket', 'rocket', 'rocket'], 
    menu_icon="cast", default_index=0, orientation="horizontal")

if selected2 == "RSI":

 # Define the symbol and interval as selectboxes
  market = st.text_input("Enter market symbol (e.g. BTCUSDT)", "BTCUSDT").upper()

  tick_interval = st.selectbox("Select tick interval", ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w"])

 # Make API request
  url = 'https://api.binance.us/api/v3/klines?symbol='+market+'&interval='+tick_interval
  response = requests.get(url)

  if response.status_code == 200:
    # Parse response data into a DataFrame
    data = response.json()
    data_df = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"])
    data_df["Open time"] = pd.to_datetime(data_df["Open time"], unit="ms")
    data_df.set_index("Open time", inplace=True)
    # Calculate technical indicators
    data_df[['Open', 'High', 'Low', 'Close', 'Volume']] = data_df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)

    
   

    rsi_length = st.slider('Select RSI length', min_value=2, max_value=len(data_df), value=14, step=1)
    rsi_buy_threshold = st.slider('Select RSI buy threshold', min_value=0, max_value=100, value=20, step=1)
    rsi_sell_threshold = st.slider('Select RSI sell threshold', min_value=0, max_value=100, value=70, step=1)
    data_df['RSI'] = ta.rsi(data_df['Close'], length=rsi_length)

    # Define entry points
    entry_points = data_df['RSI'] < rsi_buy_threshold  # Buy when RSI is below the buy threshold
    exit_points = data_df['RSI'] > rsi_sell_threshold  # Sell when RSI is above the sell threshold

    #stop_lose = st.slider('STOP LOSE 0.001 =1% /0.002 = 2%/ 0.01 =10%',min_value=0.001,max_value=0.01,value=0.001,step=1)

    #entries = ta.cross(data_df['EMA'], data_df['EMA2'])
    #exits = ta.cross(data_df['EMA2'], data_df['EMA'])
  
    stop_lose = st.slider('Select stop loss percentage', min_value=0, max_value=100, value=1, step=1, format='%d%%') / 100



    # Build portfolio from signals
    pf = vbt.Portfolio.from_signals(
        data_df.Close,
        entries=entry_points,
        exits=exit_points,
        sl_stop =stop_lose,
        init_cash=100_000,
        freq='D'
    )
    #############################################################################################
  
    # Plot orders using Vectorbt
    er = pf.plot_positions()

    fig = pf.plot_orders()

    total = pf.total_benchmark_return()

    
    # Display plot in Streamlit

    st.plotly_chart(fig)
    st.plotly_chart(er)
    st.write("percentage return",total)
    
  else:
    st.write("Error:", response.status_code)

if selected2 == "Ema Crossover":
 

 # Define the symbol and interval as selectboxes
 market = st.text_input("Enter market symbol (e.g. BTCUSDT)", "BTCUSDT").upper()

 tick_interval = st.selectbox("Select tick interval", ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w"])

 # Make API request
 url = 'https://api.binance.us/api/v3/klines?symbol='+market+'&interval='+tick_interval
 response = requests.get(url)

 if response.status_code == 200:
    # Parse response data into a DataFrame
    data = response.json()
    data_df = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"])
    data_df["Open time"] = pd.to_datetime(data_df["Open time"], unit="ms")
    data_df.set_index("Open time", inplace=True)
    # Calculate technical indicators
    data_df[['Open', 'High', 'Low', 'Close', 'Volume']] = data_df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)

     

    
    ema_length = st.slider('Select EMA length', min_value=2, max_value=len(data_df), value=20, step=1)
    data_df['EMA'] = ta.ema(data_df['Close'], length=ema_length)

    ema_length = st.slider('Select EMA2 length', min_value=2, max_value=len(data_df), value=20, step=1)
    data_df['EMA2'] = ta.ema(data_df['Close'], length=ema_length)


    entries = ta.cross(data_df['EMA'], data_df['EMA2'])
    exits = ta.cross(data_df['EMA2'], data_df['EMA'])
     
    
  

   # data_df['RSI'] = ta.rsi(data_df['Close'], length=14)
    #entries = ta.cross(data_df['EMA'], data_df['EMA2'])
    #exits = ta.cross(data_df['EMA2'], data_df['EMA'])
  
    
    # Build portfolio from signals
    pf = vbt.Portfolio.from_signals(
        data_df.Close,
        entries=entries,
        exits=exits,
        init_cash=100_000,
        freq='D'
    )
    
    # Plot orders using Vectorbt
    er = pf.plot_positions()

    fig = pf.plot_orders()

    total = pf.total_benchmark_return()

    
    # Display plot in Streamlit
    st.plotly_chart(fig)
    st.plotly_chart(er)
    st.write("percentage return",total)
    
 else:
    st.write("Error:", response.status_code)

