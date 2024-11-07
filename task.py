import pyotp
import requests
import threading
import yfinance as yf
from time import sleep
from datetime import datetime
from zoneinfo import ZoneInfo
from SmartApi import SmartConnect
from stock.models import StockConfig
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from helper.angel_socket import LTP_Action, connect_to_socket
from moneyball.settings import BED_URL_DOMAIN, BROKER_API_KEY, BROKER_PIN, BROKER_TOTP_KEY, BROKER_USER_ID, SOCKET_STREAM_URL_DOMAIN, broker_connection, sws, open_position


def stay_awake():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'Stay Awake: Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')
    url = f"{SOCKET_STREAM_URL_DOMAIN}/api/system_conf/awake/"
    x = requests.get(url, verify=False)
    print(f'Stay Awake: Execution Time(hh:mm:ss): {url} : {x.status_code} : {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def BrokerConnection():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        print(f'MoneyBall: Broker Connection: Started')
        global broker_connection
        try:
            broker_connection.terminateSession(BROKER_USER_ID)
        except Exception as e:
            print(f'MoneyBall: Broker Connection: Trying to Terminate Session Error: {e}')
        
        connection = SmartConnect(api_key=BROKER_API_KEY)
        connection.generateSession(BROKER_USER_ID, BROKER_PIN, totp=pyotp.TOTP(BROKER_TOTP_KEY).now())
        broker_connection = connection
    except Exception as e:
        print(f'MoneyBall: Broker Connection: Error: {e}')
    print(f'MoneyBall: Broker Connection: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def stop_socket_setup(log_identifier='Cron'):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'MoneyBall: Stop Socket Setup : {log_identifier} : Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')

    global sws
    try:
        sleep(2)
        sws.close_connection()
        sws = None
        print(f'MoneyBall: Stop Socket Setup : {log_identifier} : Connection Closed')
        sleep(2)
    except Exception as e:
        print(f'MoneyBall: Stop Socket Setup : {log_identifier} : Trying to close the connection : {e}')
    print(f'MoneyBall: Stop Socket Setup : {log_identifier} : Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def socket_setup(log_identifier='Cron'):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'MoneyBall: Socket Setup : {log_identifier} : Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')

    global broker_connection, sws, open_position
    sleep(2)

    BROKER_AUTH_TOKEN = broker_connection.access_token
    BROKER_FEED_TOKEN = broker_connection.feed_token

    new_sws = SmartWebSocketV2(BROKER_AUTH_TOKEN, BROKER_API_KEY, BROKER_USER_ID, BROKER_FEED_TOKEN)
    sleep(2)
    sws = new_sws

    correlation_id = "moneyball-socket"
    mode = 1
    nse = []
    nfo = []
    bse = []
    bfo = []
    mcx = []

    entries = StockConfig.objects.filter(is_active=True)
    for i in entries:
        open_position[i.symbol.token] = False
        # if i.symbol.exchange == 'NSE':
        #     nse.append(i.symbol.token)
        if i.symbol.exchange == 'NFO':
            nfo.append(i.symbol.token)
        # elif i.symbol.exchange == 'BSE':
        #     bse.append(i.symbol.token)
        elif i.symbol.exchange == 'BFO':
            bfo.append(i.symbol.token)
        # else:
        #     mcx.append(i.symbol.token)

    subscribe_list = []
    for index, i in enumerate((nse,nfo,bse,bfo,mcx)):
        if i:
            subscribe_list.append({
                "exchangeType": index+1,
                "tokens": i
            })
    print(f'MoneyBall: Socket Setup : {log_identifier} : Subscribe List : {subscribe_list}')
    # if not entries:
    #     subscribe_list.append({
    #             "exchangeType": 1,
    #             "tokens": '3045'
    #         })
    
    # Streaming threads for Open Positions
    socket_thread = threading.Thread(name=f"Streaming-{now.strftime('%d-%b-%Y %H:%M:%S')}", target=connect_to_socket, args=(correlation_id, mode, subscribe_list), daemon=True)
    socket_thread.start()

    print(f'MoneyBall: Socket Setup : {log_identifier} : Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def CheckLtp():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'MoneyBall: Check LTP : Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')

    global sws, open_position
    correlation_id = "moneyball-socket"
    socket_mode = 1
    try:
        symbol_obj_list = StockConfig.objects.filter(symbol__product='equity')
        symbol_list = { f"{sym.symbol.name}.NS":sym.symbol.token for sym in symbol_obj_list }
        tickers = yf.Tickers(list(symbol_list.keys())).tickers
        for ticker in tickers:
            try:
                ltp = tickers[ticker].info.get('currentPrice')
                LTP_Action(symbol_list[ticker], ltp, open_position, correlation_id, socket_mode, sws)
            except Exception as e:
                print(f'MoneyBall: Check LTP : Error Loop: {ticker} : {ltp} : {e}')
    except Exception as e:
        print(f'MoneyBall: Check LTP : Error Main : {e}')
    print(f'MoneyBall: Check LTP : Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True