import pytz
import pandas as pd
from datetime import datetime
from moneyball.settings import broker_connection, account_connections

def historical_data(token, exchange, now, from_day, interval):
    historicParam = {
        "exchange": exchange,
        "symboltoken": token,
        "interval": interval,
        "fromdate": from_day.strftime("%Y-%m-%d %H:%M"),
        "todate": now.strftime("%Y-%m-%d %H:%M")
    }
    global broker_connection
    connection = None
    if account_connections:
        if exchange == 'NSE':
            connection = account_connections.get('P567723')
        if exchange == 'NFO':
            connection = account_connections.get('H188598')
    if connection is None:
        connection = broker_connection
    data = pd.DataFrame(connection.getCandleData(historicParam)['data'])
    data.rename(columns={
        0: 'date', 1: 'Open', 2: 'High', 3: 'Low', 4: 'Close', 5: 'Volume'}, inplace=True)
    data.index.names = ['date']
    data_frame = data
    # Convert str timestamps to IST
    ist_timezone = pytz.timezone('Asia/Kolkata')
    data_frame['date'] = data_frame['date'].apply(lambda x: datetime.fromisoformat(x).astimezone(ist_timezone))

    data_frame = data_frame.fillna(data_frame.mean())
    return data_frame
