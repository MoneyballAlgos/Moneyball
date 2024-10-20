import pandas_ta as ta
from ta.momentum import rsi, stochrsi_d, stochrsi_k
from ta.volatility import average_true_range, BollingerBands, KeltnerChannel
from ta.trend import ema_indicator, macd_diff, macd_signal, macd, sma_indicator

def EMA(dataframe, timeperiod):
    return ema_indicator(close=dataframe,
                         window=timeperiod)


def SMA(dataframe, timeperiod):
    return sma_indicator(close=dataframe,
                         window=timeperiod)


def ADX(high, low, close, timeperiod):
    return ta.adx(high=high,
               low=low,
               close=close,
               length=timeperiod)[f"ADX_{timeperiod}"]


def SUPER_TREND(high, low, close, length, multiplier):
    return ta.supertrend(high=high,
               low=low,
               close=close,
               length=length,
               multiplier=multiplier)[f"SUPERT_{length}_{multiplier}.0"]


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