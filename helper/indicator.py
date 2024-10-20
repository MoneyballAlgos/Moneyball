import numpy as np
import pandas as pd
from ta.momentum import rsi, stochrsi_d, stochrsi_k
from ta.volatility import average_true_range, BollingerBands, KeltnerChannel
from ta.trend import ema_indicator, macd_diff, macd_signal, macd, sma_indicator

def EMA(dataframe, timeperiod):
    return ema_indicator(close=dataframe,
                         window=timeperiod)


def SMA(dataframe, timeperiod):
    return sma_indicator(close=dataframe,
                         window=timeperiod)


def SUPER_TREND(high, low, close, length, multiplier):
    # ATR
    
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
    atr = tr.ewm(length).mean()
    
    # H/L AVG AND BASIC UPPER & LOWER BAND
    
    hl_avg = (high + low) / 2
    upper_band = (hl_avg + multiplier * atr).dropna()
    lower_band = (hl_avg - multiplier * atr).dropna()
    
    # FINAL UPPER BAND
    final_bands = pd.DataFrame(columns = ['upper', 'lower'])
    final_bands.iloc[:,0] = [x for x in upper_band - upper_band]
    final_bands.iloc[:,1] = final_bands.iloc[:,0]
    for i in range(len(final_bands)):
        if i == 0:
            final_bands.iloc[i,0] = 0
        else:
            if (upper_band[i] < final_bands.iloc[i-1,0]) | (close[i-1] > final_bands.iloc[i-1,0]):
                final_bands.iloc[i,0] = upper_band[i]
            else:
                final_bands.iloc[i,0] = final_bands.iloc[i-1,0]
    
    # FINAL LOWER BAND
    
    for i in range(len(final_bands)):
        if i == 0:
            final_bands.iloc[i, 1] = 0
        else:
            if (lower_band[i] > final_bands.iloc[i-1,1]) | (close[i-1] < final_bands.iloc[i-1,1]):
                final_bands.iloc[i,1] = lower_band[i]
            else:
                final_bands.iloc[i,1] = final_bands.iloc[i-1,1]
    
    # SUPERTREND
    
    supertrend = pd.DataFrame(columns = [f'supertrend_{length}'])
    supertrend.iloc[:,0] = [x for x in final_bands['upper'] - final_bands['upper']]
    
    for i in range(len(supertrend)):
        if i == 0:
            supertrend.iloc[i, 0] = 0
        elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 0] and close[i] < final_bands.iloc[i, 0]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 0]
        elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 0] and close[i] > final_bands.iloc[i, 0]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
        elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 1] and close[i] > final_bands.iloc[i, 1]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
        elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 1] and close[i] < final_bands.iloc[i, 1]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 0]
    
    supertrend = supertrend.set_index(upper_band.index)
    supertrend = supertrend.dropna()[1:]

    return supertrend[f"supertrend_{length}"]


def MACD(close, fast, slow, signal):
    macd_diff_df = macd(close=close,
                        window_fast=fast,
                        window_slow=slow)
    macd_signal_df = macd_signal(close=close,
                                 window_fast=fast,
                                 window_slow=slow,
                                 window_sign=signal)
    macd_hist_df = macd_diff(close=close,
                             window_fast=fast,
                             window_slow=slow,
                             window_sign=signal)
    return {'diff': macd_diff_df, 'signal': macd_signal_df, 'hist': macd_hist_df}


def RSI(close, timeperiod):
    return rsi(close=close, window=timeperiod)


def ATR(high, low, close, timeperiod):
    return average_true_range(high=high, low=low,close=close, window=timeperiod)


def SRSI(close, timeperiod):
    srsi_k = stochrsi_k(close=close,
                        window=timeperiod)
    srsi_d = stochrsi_d(close=close,
                        window=timeperiod)
    return {'srsi_k': srsi_k, 'srsi_d': srsi_d}


def BB(close, timeperiod, std_dev):
    # Initialize Bollinger Bands Indicator
    indicator_bb = BollingerBands(close, window=timeperiod, window_dev=std_dev)

    # Add Bollinger Bands features
    hband = indicator_bb.bollinger_hband()
    mband = indicator_bb.bollinger_mavg()
    lband = indicator_bb.bollinger_lband()

    # Add Bollinger Band high indicator
    hbandi = indicator_bb.bollinger_hband_indicator()

    # Add Bollinger Band low indicator
    lbandi = indicator_bb.bollinger_lband_indicator()

    # Add Width Size Bollinger Bands
    wband = indicator_bb.bollinger_wband()

    # Add Percentage Bollinger Bands
    pband = indicator_bb.bollinger_pband()

    return {'hband': hband, 'mband': mband, 'lband': lband, 'hbandi': hbandi, 'lbandi': lbandi, 'wband': wband, 'pband': pband}


def KC(high, low, close, timeperiod, std_dev, atr):
    # Initialize Keltner Channel Indicator
    indicator_kc = KeltnerChannel(high, low, close, window=timeperiod, multiplier=std_dev, window_atr=atr, original_version=False)

    # Add Keltner Channel features
    hband = indicator_kc.keltner_channel_hband()
    mband = indicator_kc.keltner_channel_mband()
    lband = indicator_kc.keltner_channel_lband()

    # Add Keltner Channel high indicator
    hbandi = indicator_kc.keltner_channel_hband_indicator()

    # Add Keltner Channel low indicator
    lbandi = indicator_kc.keltner_channel_lband_indicator()

    # Add Width Size Keltner Channel
    wband = indicator_kc.keltner_channel_wband()

    # Add Percentage Keltner Channel
    pband = indicator_kc.keltner_channel_pband()

    return {'hband': hband, 'mband': mband, 'lband': lband, 'hbandi': hbandi, 'lbandi': lbandi, 'wband': wband, 'pband': pband}


def PIVOT(last_day_data_frame):
    pivot = (last_day_data_frame['High'] + last_day_data_frame['Low'] + last_day_data_frame['Close'])/3
    R1 = 2*pivot - last_day_data_frame['Low']
    S1 = 2*pivot - last_day_data_frame['High']
    R2 = pivot + (last_day_data_frame['High'] - last_day_data_frame['Low'])
    S2 = pivot - (last_day_data_frame['High'] - last_day_data_frame['Low'])
    R3 = pivot + 2*(last_day_data_frame['High'] - last_day_data_frame['Low'])
    S3 = pivot - 2*(last_day_data_frame['High'] - last_day_data_frame['Low'])

    return {'pivot': pivot, 'r1': R1, 's1': S1, 'r2': R2, 's2': S2, 'r3': R3, 's3': S3}