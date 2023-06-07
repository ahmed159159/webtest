import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta
import vectorbt as vbt
import talib
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
  url = 'https://api.binance.com/api/v3/klines?symbol='+market+'&interval='+tick_interval
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
 url = 'https://api.binance.com/api/v3/klines?symbol='+market+'&interval='+tick_interval
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
if selected2 == "candel":
 exchange_info_url = 'https://api.binance.com/api/v3/exchangeInfo'
 symbols_data = requests.get(exchange_info_url).json()
 symbols = [symbol['symbol'] for symbol in symbols_data['symbols']]

 # Specify the available candlestick time frames
 candlestick_time_frames = {
    '1m': '1 minute',
    '5m': '5 minutes',
    '15m': '15 minutes',
    '30m': '30 minutes',
    '1h': '1 hour',
    '4h': '4 hours',
    '1d': '1 day',
    '1w': '1 week',
 }

 # Specify the available candlestick patterns
 candlestick_patterns = {
    'CDLDOJI': 'Doji',
    'CDLDOJISTAR':'Doji Star',
    'CDLHAMMER': 'Hammer',
    'CDLHANGINGMAN': 'Hanging Man',
    'CDLINVHAMMER': 'Inverted Hammer',
    'CDLSHOOTINGSTAR': 'Shooting Star',
    'CDL2CROWS' : 'Two Crows',
    'CDL3BLACKCROWS' : 'Three Black Crows',
    'CDL3INSIDE' : 'Three Inside Up/Down',
    'CDL3LINESTRIKE' : 'Three-Line Strike',
    'CDL3OUTSIDE' : 'Three Outside Up/Down',
    'CDL3STARSINSOUTH' : 'Three Stars In The South',
    'CDL3WHITESOLDIERS' : 'Three Advancing White Soldiers',
    'CDLABANDONEDBABY' : 'Abandoned Baby',
    'CDLADVANCEBLOCK' : 'Advance Block',
    'CDLBELTHOLD' : 'Belt-hold',
    'CDLBREAKAWAY' : 'Breakaway',
    'CDLCLOSINGMARUBOZU' :'Closing Marubozu',
    'CDLCONCEALBABYSWALL' : 'Concealing Baby Swallow',
    'CDLCOUNTERATTACK' :'Counterattack',
    'CDLDARKCLOUDCOVER' :'Dark Cloud Cover',
    'CDLDRAGONFLYDOJI' : 'Dragonfly Doji',
    'CDLENGULFING' : 'Engulfing Pattern',
    'CDLEVENINGDOJISTAR' : 'Evening Doji Star',
    'CDLEVENINGSTAR ': 'Evening Star',
    'CDLGAPSIDESIDEWHITE' : 'Up/Down-gap side-by-side white lines',
    'CDLGRAVESTONEDOJI' : 'Gravestone Doji',
    'CDLHARAMICROSS' : 'Harami Cross Pattern',
    'CDLHIGHWAVE' : 'High-Wave Candle',
    'CDLHIKKAKE' :'Hikkake Pattern',
    'CDLHIKKAKEMOD' : 'Modified Hikkake Pattern',
    'CDLHOMINGPIGEON' : 'Homing Pigeon',
    'CDLIDENTICAL3CROWS' :'Identical Three Crows',
    'CDLINNECK' :'In-Neck Pattern',
    'CDLINVERTEDHAMMER' :'Inverted Hammer',
    'CDLKICKING' : 'Kicking',
    'CDLKICKINGBYLENGTH' :'Kicking - bull/bear determined by the longer marubozu',
    'CDLLADDERBOTTOM' :'Ladder Bottom',
    'CDLLONGLEGGEDDOJI' :'Long Legged Doji',
    'CDLLONGLINE' :'Long Line Candle',
    'CDLMARUBOZU' :'Marubozu',
    'CDLMATCHINGLOW' :'Matching Low',
    'CDLMATHOLD' :'Mat Hold',
    'CDLMORNINGDOJISTAR' :'Morning Doji Star',
    'CDLMORNINGSTAR' :'Morning Star',
    'CDLONNECK' :'On-Neck Pattern',
    'CDLPIERCING' :'Piercing Pattern',
    'CDLRICKSHAWMAN' :'Rickshaw Man',
    'CDLRISEFALL3METHODS' :'Rising/Falling Three Methods',
    'CDLSEPARATINGLINES' :'Separating Lines',
    'CDLSHOOTINGSTAR' :'Shooting Star',
    'CDLSHORTLINE' : 'Short Line Candle',
    'CDLSPINNINGTOP' :'Spinning Top',
    'CDLSTALLEDPATTERN' :'Stalled Pattern',
    'CDLSTICKSANDWICH' :'Stick Sandwich',
    'CDLTAKURI' :'Takuri',
    'CDLTASUKIGAP' :'Tasuki Gap',
    'CDLTHRUSTING' :'Thrusting Pattern',
    'CDLTRISTAR':'Tristar Pattern',
    'CDLUNIQUE3RIVER':'Unique 3 River',
    'CDLUPSIDEGAP2CROWS':'Upside Gap Two Crows',
    'CDLXSIDEGAP3METHODS': 'Upside/Downside Gap Three Methods'



 }

 # Specify the available base assets
 base_assets = ['USDT', 'BNB', 'ETH', 'BTC']

 # Create a Streamlit app
 st.title('Binance Candlestick Pattern Scanner')

 # Add a drop-down menu to select the base asset
 selected_base_asset = st.selectbox('Select Base Asset', options=base_assets)

 # Add a drop-down menu to select the candlestick time frame
 selected_time_frame = st.selectbox('Select Candlestick Time Frame', options=list(candlestick_time_frames.keys()))

 # Add checkboxes for selecting candlestick patterns
 selected_patterns = st.multiselect('Select Candlestick Patterns', options=list(candlestick_patterns.keys()))

 # Filter symbols based on selected base asset
 filtered_symbols = [symbol for symbol in symbols if symbol.endswith(selected_base_asset)]

 # Loop through each filtered symbol and fetch historical candlestick data
 for symbol in filtered_symbols:
    try:
        url = 'https://api.binance.com/api/v3/klines?symbol='+symbol+'&interval='+selected_time_frame
        data = requests.get(url).json()
        data_df = pd.DataFrame(data)

        # Extract OHLCV data from the raw data
        ohlcvs = data_df.iloc[:, :6]
        ohlcvs.columns = ['timestamp', 'o', 'h', 'l', 'c', 'v']

        # Convert timestamp to datetime
        ohlcvs['timestamp'] = pd.to_datetime(ohlcvs['timestamp'], unit='ms')
        ohlcvs.set_index('timestamp', inplace=True)

        # Convert OHLCV data to float
        ohlcvs['o'] = ohlcvs['o'].astype(float)
        ohlcvs['h'] = ohlcvs['h'].astype(float)
        ohlcvs['l'] = ohlcvs['l'].astype(float)
        ohlcvs['c'] = ohlcvs['c'].astype(float)
        ohlcvs['v'] = ohlcvs['v'].astype(float)
        
        # Get last closed candle
        last_candle = ohlcvs.iloc[-1]

        # Check if last closed candle matches selected candlestick pattern
        for pattern in selected_patterns:
            pattern_func = getattr(talib, pattern)
            pattern_result = pattern_func(ohlcvs['o'], ohlcvs['h'], ohlcvs['l'], ohlcvs['c'])
            if pattern_result.iloc[-1] != 0:
                st.write(f'Symbol: {symbol}')
                st.write(f'Last Closed Candle: {last_candle.name}')
                st.write(f'Candlestick Pattern: {candlestick_patterns[pattern]}')

    except Exception as e:
        st.write(f'Error occurred for symbol {symbol}: {e}')
