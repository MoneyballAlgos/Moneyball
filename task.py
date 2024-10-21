import pyotp
import requests
from time import sleep
from zoneinfo import ZoneInfo
from SmartApi import SmartConnect
from datetime import datetime, time, timedelta
from helper.angel_function import historical_data
from stock.models import StockConfig, Transaction
from helper.indicator import BB, PIVOT, SUPER_TREND
from system_conf.models import Configuration, Symbol
from helper.common import calculate_volatility, last_thursday
from helper.trade_action import Price_Action_Trade, Stock_Square_Off
from account.models import AccountConfiguration, AccountKeys, AccountStockConfig, AccountTransaction
from moneyball.settings import BED_URL_DOMAIN, BROKER_API_KEY, BROKER_PIN, BROKER_TOTP_KEY, BROKER_USER_ID, SOCKET_STREAM_URL_DOMAIN, broker_connection, account_connections, entry_holder


def stay_awake():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'Stay Awake: Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')
    x = requests.get(f"{BED_URL_DOMAIN}/api/system_conf/awake", verify=False)
    print(f'Stay Awake: Execution Time(hh:mm:ss): {x.status_code} : {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def MarketDataUpdate():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        print(f'MoneyBall: Market data Update: Started : Runtime : {now.strftime("%d-%b-%Y %H:%M:%S")}')
        if now.time().minute in list(range(0, 60, 5)):
            sleep(10)
        nse_tokens = list(Symbol.objects.filter(exchange='NSE', is_active=True).values_list('token', flat=True))
        token_list = [nse_tokens[x:x+50] for x in range(0, len(nse_tokens), 50)]
        global broker_connection
        for list_ in token_list:
            try:
                data = broker_connection.getMarketData(mode="FULL", exchangeTokens={"NSE": list_})
                if data.get('data'):
                    fetched = data.get('data')['fetched']
                    for i in fetched:
                        if now.time() > time(8, 00, 00) and now.time() < time(9, 14, 00):
                            Symbol.objects.filter(token=i['symbolToken'],
                                                    is_active=True).update(
                                                        volume=i['tradeVolume'],
                                                        oi=i['opnInterest'],
                                                        percentchange=i['percentChange'],
                                                        valuechange=i['netChange'],
                                                        ltp=i['ltp'],
                                                        weekhigh52=i['52WeekHigh'],
                                                        weeklow52=i['52WeekLow']
                                                    )
                        else:
                            Symbol.objects.filter(token=i['symbolToken'],
                                                    is_active=True).update(
                                                        volume=i['tradeVolume'],
                                                        oi=i['opnInterest'],
                                                        percentchange=i['percentChange'],
                                                        valuechange=i['netChange'],
                                                        ltp=i['ltp']
                                                    )
                sleep(1)
            except Exception as e:
                print(f'MoneyBall: Market data Update: Loop Error: {e}')
    except Exception as e:
        print(f'MoneyBall: Market data Update: Main Error: {e}')
    print(f'MoneyBall: Market data Update: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def SymbolSetup():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:

        print(f'MoneyBall: Awake the Socket Service: Started')
        x = requests.get(f"{SOCKET_STREAM_URL_DOMAIN}/api/system_conf/awake", verify=False)
        print(f'MoneyBall: Awake the Socket Service: Execution Time(hh:mm:ss): {x.status_code} : {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')

        print(f'MoneyBall: Symbol Setup: Started')
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        data = requests.get(url).json()

        open_entries_symbols = StockConfig.objects.filter(is_active=True).values_list('symbol__symbol', flat=True)
        Symbol.objects.filter(is_active=True).exclude(symbol__in=open_entries_symbols).delete()

        Symbol.objects.filter(expiry__lt=now.date(), is_active=True).delete()

        exclude_symbol = ['HDFCNIFTY', '031NSETEST', '151NSETEST', 'LIQUID', 'HNGSNGBEES', 'AXISCETF', 'SETFNIFBK', 'EBANKNIFTY', '171NSETEST', 'SETFNIF50', 'CPSEETF', 'GSEC10IETF', 'DIVOPPBEES', 'OILIETF', 'AUTOIETF', 'HDFCLIQUID', 'AXISNIFTY', 'NIFTY50ADD', 'CONSUMBEES', 'HDFCNIFBAN', 'NIFTYBEES', '101NSETEST', 'LIQUIDETF', 'TOP10ADD', 'NIF100BEES', 'PSUBNKIETF', 'INFRABEES', 'AXISTECETF', 'NV20BEES', 'ALPL30IETF', 'INFRAIETF', '181NSETEST', 'MOM30IETF', 'SBISILVER', 'NIFTY1', 'UTINIFTETF', 'SILVERBEES', 'BANKETFADD', 'MIDCAPIETF', 'PHARMABEES', 'SENSEXADD', 'GOLDCASE', 'HEALTHIETF', 'BSLNIFTY', 'PVTBANIETF', 'BSE500IETF', '071NSETEST', '011NSETEST', 'IVZINGOLD', 'NETF', 'SENSEXIETF', 'SBIETFIT', 'ABSLBANETF', 'SILVERTUC', 'SHARIABEES', 'EBBETF0433', 'SILVERETF', 'FMCGIETF', 'NIF10GETF', '021NSETEST', 'CONSUMIETF', 'SILVERIETF', 'SETF10GILT', 'NV20IETF', 'SDL26BEES', 'SENSEXETF', 'NIF100IETF', 'QNIFTY', 'MIDSELIETF', 'BBNPPGOLD', 'SBINEQWETF', 'NIFTYIETF', 'LIQUIDIETF', 'ITBEES', 'LICNETFSEN', '121NSETEST', '051NSETEST', 'ITETF', 'NIFTYETF', 'SILVER', 'EQUAL50ADD', 'UTISENSETF', 'QUAL30IETF', 'AXISGOLD', 'AXISHCETF', 'ALPHAETF', 'HDFCNIF100', 'PSUBNKBEES', 'BSLSENETFG', '041NSETEST', 'QGOLDHALF', 'BBETF0432', 'COMMOIETF', 'MONIFTY500', 'BBNPNBETF', 'LIQUIDCASE', 'GINNIFILA', 'GOLDIAM', 'NAVINIFTY', 'ITIETF', 'SILVER1', '131NSETEST', 'SBIETFPB', 'LICNETFN50', 'BANKBEES', 'METALIETF', 'AUTOBEES', 'ITETFADD', 'SILVERADD', 'HEALTHADD', 'GOLDSHARE', 'LIQUID1', 'AXISBPSETF', 'IVZINNIFTY', 'GILT5YBEES', '111NSETEST', 'HDFCGOLD', 'SILVRETF', 'GOLDTECH', 'BANKETF', 'LICNETFGSC', 'LTGILTBEES', 'GOLD1', 'BANKNIFTY1', '161NSETEST', 'ABSLLIQUID', 'GSEC5IETF', 'LIQUIDBETF', '061NSETEST', 'BANKIETF', 'LIQUIDSHRI', 'AXISILVER', 'UTIBANKETF', 'IDFNIFTYET', 'MIDCAPETF', 'GOLDBEES', 'FINIETF', 'EBBETF0425', 'PVTBANKADD', 'NEXT50IETF', 'ESILVER', 'GOLDETFADD', 'BANKBETF', 'JUNIORBEES', 'PSUBANKADD', 'MIDQ50ADD', 'HDFCNIFIT', 'GOLDIETF', 'EBBETF0430', 'NIF5GETF', 'BSLGOLDETF', 'EBBETF0431', 'LIQUIDSBI', 'EGOLD', 'TATAGOLD', 'TNIDETF', 'SBIETFQLTY', 'NIFITETF', 'LOWVOLIETF', 'SDL24BEES', '081NSETEST', 'GOLDETF', 'SETFGOLD', 'AXISBNKETF', 'NIFTYQLITY', 'LIQUIDADD', '141NSETEST', 'SBIETFCON', 'LIQUIDBEES', 'MID150BEES', 'SETFNN50', 'NIFMID150', '091NSETEST', 'HDFCSILVER', 'NIFTYBETF', 'LICMFGOLD', 'MOM100', 'TOP100CASE', 'MON100', 'LICNMID100', 'MIDSMALL', 'MIDCAP', 'MID150CASE', 'HDFCMID150', 'HDFCNEXT50', 'UTISXN50', 'MONQ50', 'MOM50', 'ABSLNN50ET', 'HDFCSML250', 'NEXT50', 'HDFCBSE500', 'MOSMALL250', 'UTINEXT50', 'MASPTOP50', 'HDFCSENSEX', 'AXSENSEX', '11NSETEST']

        Symbol.objects.filter(name__in=exclude_symbol, is_active=True).delete()

        last_thursday_date = last_thursday(now)
        if last_thursday_date.date() < now.date():
            month_num = now.month + 1
        else:
            month_num = now.month

        print(f'MoneyBall: Symbol Setup: Fetch Index Symbol List : Started')

        nifty50 = ['ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BEL', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'ITC', 'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 'NTPC', 'NESTLEIND', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE', 'SHRIRAMFIN', 'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'TRENT', 'ULTRACEMCO', 'WIPRO']
        
        nifty100 = ['ABB', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ADANIPOWER', 'ATGL', 'AMBUJACEM', 'APOLLOHOSP', 'ASIANPAINT', 'DMART', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BAJAJHLDNG', 'BANKBARODA', 'BEL', 'BHEL', 'BPCL', 'BHARTIARTL', 'BOSCHLTD', 'BRITANNIA', 'CANBK', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'DLF', 'DABUR', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GAIL', 'GODREJCP', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HAVELLS', 'HEROMOTOCO', 'HINDALCO', 'HAL', 'HINDUNILVR', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'ITC', 'IOC', 'IRCTC', 'IRFC', 'INDUSINDBK', 'NAUKRI', 'INFY', 'INDIGO', 'JSWENERGY', 'JSWSTEEL', 'JINDALSTEL', 'JIOFIN', 'KOTAKBANK', 'LTIM', 'LT', 'LICI', 'LODHA', 'M&M', 'MARUTI', 'NHPC', 'NTPC', 'NESTLEIND', 'ONGC', 'PIDILITIND', 'PFC', 'POWERGRID', 'PNB', 'RECLTD', 'RELIANCE', 'SBILIFE', 'MOTHERSON', 'SHREECEM', 'SHRIRAMFIN', 'SIEMENS', 'SBIN', 'SUNPHARMA', 'TVSMOTOR', 'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TECHM', 'TITAN', 'TORNTPHARM', 'TRENT', 'ULTRACEMCO', 'UNIONBANK', 'UNITDSPR', 'VBL', 'VEDL', 'WIPRO', 'ZOMATO', 'ZYDUSLIFE']
        
        nifty200 = ['ABB', 'ACC', 'APLAPOLLO', 'AUBANK', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ADANIPOWER', 'ATGL', 'ABCAPITAL', 'ABFRL', 'ALKEM', 'AMBUJACEM', 'APOLLOHOSP', 'APOLLOTYRE', 'ASHOKLEY', 'ASIANPAINT', 'ASTRAL', 'AUROPHARMA', 'DMART', 'AXISBANK', 'BSE', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BAJAJHLDNG', 'BALKRISIND', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'MAHABANK', 'BDL', 'BEL', 'BHARATFORG', 'BHEL', 'BPCL', 'BHARTIARTL', 'BHARTIHEXA', 'BIOCON', 'BOSCHLTD', 'BRITANNIA', 'CGPOWER', 'CANBK', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'COCHINSHIP', 'COFORGE', 'COLPAL', 'CONCOR', 'CUMMINSIND', 'DLF', 'DABUR', 'DELHIVERY', 'DIVISLAB', 'DIXON', 'DRREDDY', 'EICHERMOT', 'ESCORTS', 'EXIDEIND', 'NYKAA', 'FEDERALBNK', 'FACT', 'GAIL', 'GMRINFRA', 'GODREJCP', 'GODREJPROP', 'GRASIM', 'HCLTECH', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE', 'HAVELLS', 'HEROMOTOCO', 'HINDALCO', 'HAL', 'HINDPETRO', 'HINDUNILVR', 'HINDZINC', 'HUDCO', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'IDBI', 'IDFCFIRSTB', 'IRB', 'ITC', 'INDIANB', 'INDHOTEL', 'IOC', 'IOB', 'IRCTC', 'IRFC', 'IREDA', 'IGL', 'INDUSTOWER', 'INDUSINDBK', 'NAUKRI', 'INFY', 'INDIGO', 'JSWENERGY', 'JSWINFRA', 'JSWSTEEL', 'JINDALSTEL', 'JIOFIN', 'JUBLFOOD', 'KPITTECH', 'KALYANKJIL', 'KOTAKBANK', 'LTF', 'LICHSGFIN', 'LTIM', 'LT', 'LICI', 'LUPIN', 'MRF', 'LODHA', 'M&MFIN', 'M&M', 'MRPL', 'MANKIND', 'MARICO', 'MARUTI', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'MPHASIS', 'MUTHOOTFIN', 'NHPC', 'NLCINDIA', 'NMDC', 'NTPC', 'NESTLEIND', 'OBEROIRLTY', 'ONGC', 'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'PIDILITIND', 'POLYCAB', 'POONAWALLA', 'PFC', 'POWERGRID', 'PRESTIGE', 'PNB', 'RECLTD', 'RVNL', 'RELIANCE', 'SBICARD', 'SBILIFE', 'SJVN', 'SRF', 'MOTHERSON', 'SHREECEM', 'SHRIRAMFIN', 'SIEMENS', 'SOLARINDS', 'SONACOMS', 'SBIN', 'SAIL', 'SUNPHARMA', 'SUNDARMFIN', 'SUPREMEIND', 'SUZLON', 'TVSMOTOR', 'TATACHEM', 'TATACOMM', 'TCS', 'TATACONSUM', 'TATAELXSI', 'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TATATECH', 'TECHM', 'TITAN', 'TORNTPHARM', 'TORNTPOWER', 'TRENT', 'TIINDIA', 'UPL', 'ULTRACEMCO', 'UNIONBANK', 'UNITDSPR', 'VBL', 'VEDL', 'IDEA', 'VOLTAS', 'WIPRO', 'YESBANK', 'ZOMATO', 'ZYDUSLIFE']

        midcpnifty50 = ['ACC', 'APLAPOLLO', 'AUBANK', 'ABCAPITAL', 'ALKEM', 'ASHOKLEY', 'ASTRAL', 'AUROPHARMA', 'BHARATFORG', 'CGPOWER', 'COLPAL', 'CONCOR', 'CUMMINSIND', 'DIXON', 'FEDERALBNK', 'GMRINFRA', 'GODREJPROP', 'HDFCAMC', 'HINDPETRO', 'IDFCFIRSTB', 'INDHOTEL', 'INDUSTOWER', 'KPITTECH', 'LTF', 'LUPIN', 'MRF', 'MARICO', 'MAXHEALTH', 'MPHASIS', 'MUTHOOTFIN', 'NMDC', 'OBEROIRLTY', 'OFSS', 'POLICYBZR', 'PIIND', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'POLYCAB', 'SBICARD', 'SRF', 'SAIL', 'SUNDARMFIN', 'SUPREMEIND', 'SUZLON', 'TATACOMM', 'UPL', 'IDEA', 'VOLTAS', 'YESBANK']
        
        midcpnifty100 = ['ACC', 'APLAPOLLO', 'AUBANK', 'ABCAPITAL', 'ABFRL', 'ALKEM', 'APOLLOTYRE', 'ASHOKLEY', 'ASTRAL', 'AUROPHARMA', 'BSE', 'BALKRISIND', 'BANDHANBNK', 'BANKINDIA', 'MAHABANK', 'BDL', 'BHARATFORG', 'BHARTIHEXA', 'BIOCON', 'CGPOWER', 'COCHINSHIP', 'COFORGE', 'COLPAL', 'CONCOR', 'CUMMINSIND', 'DELHIVERY', 'DIXON', 'ESCORTS', 'EXIDEIND', 'NYKAA', 'FEDERALBNK', 'FACT', 'GMRINFRA', 'GODREJPROP', 'HDFCAMC', 'HINDPETRO', 'HINDZINC', 'HUDCO', 'IDBI', 'IDFCFIRSTB', 'IRB', 'INDIANB', 'INDHOTEL', 'IOB', 'IREDA', 'IGL', 'INDUSTOWER', 'JSWINFRA', 'JUBLFOOD', 'KPITTECH', 'KALYANKJIL', 'LTF', 'LICHSGFIN', 'LUPIN', 'MRF', 'M&MFIN', 'MRPL', 'MANKIND', 'MARICO', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'MPHASIS', 'MUTHOOTFIN', 'NLCINDIA', 'NMDC', 'OBEROIRLTY', 'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'POLYCAB', 'POONAWALLA', 'PRESTIGE', 'RVNL', 'SBICARD', 'SJVN', 'SRF', 'SOLARINDS', 'SONACOMS', 'SAIL', 'SUNDARMFIN', 'SUPREMEIND', 'SUZLON', 'TATACHEM', 'TATACOMM', 'TATAELXSI', 'TATATECH', 'TORNTPOWER', 'TIINDIA', 'UPL', 'IDEA', 'VOLTAS', 'YESBANK']
        
        midcpnifty150 = ['3MINDIA', 'ACC', 'AIAENG', 'APLAPOLLO', 'AUBANK', 'ABBOTINDIA', 'AWL', 'ABCAPITAL', 'ABFRL', 'AJANTPHARM', 'ALKEM', 'APOLLOTYRE', 'ASHOKLEY', 'ASTRAL', 'AUROPHARMA', 'BSE', 'BALKRISIND', 'BANDHANBNK', 'BANKINDIA', 'MAHABANK', 'BAYERCROP', 'BERGEPAINT', 'BDL', 'BHARATFORG', 'BHARTIHEXA', 'BIOCON', 'CGPOWER', 'CRISIL', 'CARBORUNIV', 'COCHINSHIP', 'COFORGE', 'COLPAL', 'CONCOR', 'COROMANDEL', 'CUMMINSIND', 'DALBHARAT', 'DEEPAKNTR', 'DELHIVERY', 'DIXON', 'EMAMILTD', 'ENDURANCE', 'ESCORTS', 'EXIDEIND', 'NYKAA', 'FEDERALBNK', 'FACT', 'FORTIS', 'GMRINFRA', 'GICRE', 'GLAND', 'GLAXO', 'MEDANTA', 'GODREJIND', 'GODREJPROP', 'GRINDWELL', 'FLUOROCHEM', 'GUJGASLTD', 'HDFCAMC', 'HINDPETRO', 'HINDZINC', 'POWERINDIA', 'HONAUT', 'HUDCO', 'IDBI', 'IDFCFIRSTB', 'IRB', 'INDIANB', 'INDHOTEL', 'IOB', 'IREDA', 'IGL', 'INDUSTOWER', 'IPCALAB', 'JKCEMENT', 'JSWINFRA', 'JSL', 'JUBLFOOD', 'KPRMILL', 'KEI', 'KPITTECH', 'KALYANKJIL', 'LTF', 'LTTS', 'LICHSGFIN', 'LINDEINDIA', 'LLOYDSME', 'LUPIN', 'MRF', 'M&MFIN', 'MRPL', 'MANKIND', 'MARICO', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'METROBRAND', 'MSUMI', 'MPHASIS', 'MUTHOOTFIN', 'NLCINDIA', 'NMDC', 'NAM-INDIA', 'OBEROIRLTY', 'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'POLYCAB', 'POONAWALLA', 'PRESTIGE', 'PGHH', 'RVNL', 'SBICARD', 'SJVN', 'SKFINDIA', 'SRF', 'SCHAEFFLER', 'SOLARINDS', 'SONACOMS', 'STARHEALTH', 'SAIL', 'SUNTV', 'SUNDARMFIN', 'SUNDRMFAST', 'SUPREMEIND', 'SUZLON', 'SYNGENE', 'TATACHEM', 'TATACOMM', 'TATAELXSI', 'TATAINVEST', 'TATATECH', 'NIACL', 'THERMAX', 'TIMKEN', 'TORNTPOWER', 'TIINDIA', 'UNOMINDA', 'UPL', 'UBL', 'IDEA', 'VOLTAS', 'YESBANK', 'ZFCVINDIA']
        
        smallcpnifty50 = ['360ONE', 'AARTIIND', 'ARE&M', 'ANGELONE', 'APARINDS', 'ATUL', 'BSOFT', 'BLUESTARCO', 'BRIGADE', 'CESC', 'CASTROLIND', 'CDSL', 'CENTURYTEX', 'CAMS', 'CROMPTON', 'CYIENT', 'FINCABLES', 'GLENMARK', 'GESHIP', 'GSPL', 'HFCL', 'HINDCOPPER', 'IDFC', 'IIFL', 'INDIAMART', 'IEX', 'KPIL', 'KARURVYSYA', 'LAURUSLABS', 'MGL', 'MANAPPURAM', 'MCX', 'NATCOPHARM', 'NBCC', 'NCC', 'NH', 'NATIONALUM', 'NAVINFLUOR', 'PNBHOUSING', 'PVRINOX', 'PEL', 'PPLPHARMA', 'RBLBANK', 'RKFORGE', 'REDINGTON', 'SONATSOFTW', 'TEJASNET', 'RAMCOCEM', 'ZEEL', 'ZENSARTECH']
        
        smallcpnifty100 = ['360ONE', 'AADHARHFC', 'AARTIIND', 'AAVAS', 'ACE', 'AEGISLOG', 'AFFLE', 'ARE&M', 'AMBER', 'ANGELONE', 'APARINDS', 'ASTERDM', 'ATUL', 'BEML', 'BLS', 'BATAINDIA', 'BSOFT', 'BLUESTARCO', 'BRIGADE', 'CESC', 'CASTROLIND', 'CENTRALBK', 'CDSL', 'CENTURYTEX', 'CHAMBLFERT', 'CHENNPETRO', 'CAMS', 'CREDITACC', 'CROMPTON', 'CYIENT', 'DATAPATTNS', 'LALPATHLAB', 'FINCABLES', 'FSL', 'FIVESTAR', 'GRSE', 'GLENMARK', 'GODIGIT', 'GESHIP', 'GMDCLTD', 'GSPL', 'HBLPOWER', 'HFCL', 'HAPPSTMNDS', 'HINDCOPPER', 'IDFC', 'IFCI', 'IIFL', 'IRCON', 'ITI', 'INDIAMART', 'IEX', 'INOXWIND', 'INTELLECT', 'JBMA', 'J&KBANK', 'JWL', 'JYOTHYLAB', 'KPIL', 'KARURVYSYA', 'KAYNES', 'KEC', 'LAURUSLABS', 'MGL', 'MANAPPURAM', 'MCX', 'NATCOPHARM', 'NBCC', 'NCC', 'NSLNISP', 'NH', 'NATIONALUM', 'NAVINFLUOR', 'OLECTRA', 'PNBHOUSING', 'PVRINOX', 'PEL', 'PPLPHARMA', 'RBLBANK', 'RITES', 'RADICO', 'RKFORGE', 'RAYMOND', 'REDINGTON', 'SHYAMMETL', 'SIGNATURE', 'SONATSOFTW', 'SWSOLAR', 'SWANENERGY', 'TANLA', 'TTML', 'TEJASNET', 'RAMCOCEM', 'TITAGARH', 'TRIDENT', 'TRITURBINE', 'UCOBANK', 'WELSPUNLIV', 'ZEEL', 'ZENSARTECH']
        
        smallcpnifty250 = ['360ONE', 'AADHARHFC', 'AARTIIND', 'AAVAS', 'ACE', 'ABSLAMC', 'AEGISLOG', 'AFFLE', 'APLLTD', 'ALKYLAMINE', 'ALOKINDS', 'ARE&M', 'AMBER', 'ANANDRATHI', 'ANANTRAJ', 'ANGELONE', 'APARINDS', 'APTUS', 'ACI', 'ASAHIINDIA', 'ASTERDM', 'ASTRAZEN', 'ATUL', 'AVANTIFEED', 'BASF', 'BEML', 'BLS', 'BALAMINES', 'BALRAMCHIN', 'BATAINDIA', 'BIKAJI', 'BIRLACORPN', 'BSOFT', 'BLUEDART', 'BLUESTARCO', 'BBTC', 'BRIGADE', 'MAPMYINDIA', 'CCL', 'CESC', 'CIEINDIA', 'CAMPUS', 'CANFINHOME', 'CAPLIPOINT', 'CGCL', 'CASTROLIND', 'CEATLTD', 'CELLO', 'CENTRALBK', 'CDSL', 'CENTURYPLY', 'CENTURYTEX', 'CERA', 'CHALET', 'CHAMBLFERT', 'CHEMPLASTS', 'CHENNPETRO', 'CHOLAHLDNG', 'CUB', 'CLEAN', 'CAMS', 'CONCORDBIO', 'CRAFTSMAN', 'CREDITACC', 'CROMPTON', 'CYIENT', 'DOMS', 'DATAPATTNS', 'DEEPAKFERT', 'DEVYANI', 'LALPATHLAB', 'EIDPARRY', 'EIHOTEL', 'EASEMYTRIP', 'ELECON', 'ELGIEQUIP', 'ENGINERSIN', 'EQUITASBNK', 'ERIS', 'FINEORG', 'FINCABLES', 'FINPIPE', 'FSL', 'FIVESTAR', 'GRINFRA', 'GET&D', 'GRSE', 'GILLETTE', 'GLENMARK', 'GODIGIT', 'GPIL', 'GODFRYPHLP', 'GODREJAGRO', 'GRANULES', 'GRAPHITE', 'GESHIP', 'GAEL', 'GMDCLTD', 'GNFC', 'GPPL', 'GSFC', 'GSPL', 'HEG', 'HBLPOWER', 'HFCL', 'HAPPSTMNDS', 'HSCL', 'HINDCOPPER', 'HOMEFIRST', 'HONASA', 'ISEC', 'IDFC', 'IFCI', 'IIFL', 'INOXINDIA', 'IRCON', 'ITI', 'INDGN', 'INDIACEM', 'INDIAMART', 'IEX', 'INOXWIND', 'INTELLECT', 'JBCHEPHARM', 'JBMA', 'JKLAKSHMI', 'JKTYRE', 'JMFINANCIL', 'JPPOWER', 'J&KBANK', 'JINDALSAW', 'JUBLINGREA', 'JUBLPHARMA', 'JWL', 'JUSTDIAL', 'JYOTHYLAB', 'JYOTICNC', 'KNRCON', 'KSB', 'KAJARIACER', 'KPIL', 'KANSAINER', 'KARURVYSYA', 'KAYNES', 'KEC', 'KFINTECH', 'KIRLOSBROS', 'KIRLOSENG', 'KIMS', 'LATENTVIEW', 'LAURUSLABS', 'LEMONTREE', 'MMTC', 'MGL', 'MAHSEAMLES', 'MAHLIFE', 'MANAPPURAM', 'MASTEK', 'METROPOLIS', 'MINDACORP', 'MOTILALOFS', 'MCX', 'NATCOPHARM', 'NBCC', 'NCC', 'NSLNISP', 'NH', 'NATIONALUM', 'NAVINFLUOR', 'NETWEB', 'NETWORK18', 'NEWGEN', 'NUVAMA', 'NUVOCO', 'OLECTRA', 'PCBL', 'PNBHOUSING', 'PNCINFRA', 'PTCIL', 'PVRINOX', 'PFIZER', 'PEL', 'PPLPHARMA', 'POLYMED', 'PRAJIND', 'QUESS', 'RRKABEL', 'RBLBANK', 'RHIM', 'RITES', 'RADICO', 'RAILTEL', 'RAINBOW', 'RAJESHEXPO', 'RKFORGE', 'RCF', 'RATNAMANI', 'RTNINDIA', 'RAYMOND', 'REDINGTON', 'ROUTE', 'SBFC', 'SAMMAANCAP', 'SANOFI', 'SAPPHIRE', 'SAREGAMA', 'SCHNEIDER', 'SCI', 'RENUKA', 'SHYAMMETL', 'SIGNATURE', 'SOBHA', 'SONATSOFTW', 'SWSOLAR', 'SUMICHEM', 'SPARC', 'SUVENPHAR', 'SWANENERGY', 'SYRMA', 'TBOTEK', 'TV18BRDCST', 'TVSSCS', 'TANLA', 'TTML', 'TECHNOE', 'TEJASNET', 'RAMCOCEM', 'TITAGARH', 'TRIDENT', 'TRIVENI', 'TRITURBINE', 'UCOBANK', 'UTIAMC', 'UJJIVANSFB', 'USHAMART', 'VGUARD', 'VIPIND', 'DBREALTY', 'VTL', 'VARROC', 'MANYAVAR', 'VIJAYA', 'VINATIORGA', 'WELCORP', 'WELSPUNLIV', 'WESTLIFE', 'WHIRLPOOL', 'ZEEL', 'ZENSARTECH', 'ECLERX']

        print(f'MoneyBall: Symbol Setup: Fetch Index Symbol List : Ended')

        bulk_create_list = []
        for i in data:
            product = None
            expity_date = datetime.strptime(i['expiry'], '%d%b%Y') if i['expiry'] else None
            if i['exch_seg'] in ['NSE', 'NFO'] and i['name'] not in exclude_symbol:
                if i['instrumenttype'] in ['OPTSTK'] and (expity_date.month == month_num): # , 'OPTIDX', 'OPTFUT'
                    product = 'future'
                elif i['symbol'].endswith('-EQ'):
                    product = 'equity'
                if product is not None:
                    bulk_create_list.append(
                        Symbol(
                            product=product,
                            name=i['name'],
                            symbol=i['symbol'],
                            token=i['token'],
                            strike=int(i['strike'].split('.')[0])/100,
                            exchange=i['exch_seg'],
                            expiry=expity_date,
                            lot=int(i['lotsize']),
                            fno=True if product == 'future' else False,
                            nifty50=True if i['name'] in nifty50 else False,
                            nifty100=True if i['name'] in nifty100 else False,
                            nifty200=True if i['name'] in nifty200 else False,
                            midcpnifty50=True if i['name'] in midcpnifty50 else False,
                            midcpnifty100=True if i['name'] in midcpnifty100 else False,
                            midcpnifty150=True if i['name'] in midcpnifty150 else False,
                            smallcpnifty50=True if i['name'] in smallcpnifty50 else False,
                            smallcpnifty100=True if i['name'] in smallcpnifty100 else False,
                            smallcpnifty250=True if i['name'] in smallcpnifty250 else False
                        )
                    )
                    if len(bulk_create_list) == 1000:
                        Symbol.objects.bulk_create(bulk_create_list)
                        print(f"MoneyBall: Symbol Setup: {Symbol.objects.filter(is_active=True).count()}")
                        bulk_create_list = []
        print(f"MoneyBall: Symbol Setup: Loop Ended")

        future_enables_symbols = set(Symbol.objects.filter(product='future', is_active=True).values_list('name', flat=True))
        Symbol.objects.filter(product='equity', name__in=future_enables_symbols, is_active=True).update(fno=True)
    except Exception as e:
        print(f'MoneyBall: Symbol Setup: Main Error: {e}')
    print(f'MoneyBall: Symbol Setup: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def AccountConnection():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:

        print(f'MoneyBall: Awake the Socket Service: Started')
        x = requests.get(f"{SOCKET_STREAM_URL_DOMAIN}/api/system_conf/awake", verify=False)
        print(f'MoneyBall: Awake the Socket Service: Execution Time(hh:mm:ss): {x.status_code} : {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')

        print(f'MoneyBall: Account Connection: Started')
        global account_connections
        try:
            print(f'MoneyBall: Account Connection: Terminate Session for accounts: Started')
            for user_id_conn in account_connections:
                account_connections[user_id_conn].terminateSession(user_id_conn)
                print(f'MoneyBall: Account Connection: Terminated Session for accounts: {user_id_conn}')
            print(f'MoneyBall: Account Connection: Terminate Session for accounts: Ended')
            sleep(5)
        except Exception as e:
            print(f'MoneyBall: Account Connection: Terminate Session for accounts: Error: {e}')
        
        print(f'MoneyBall: Account Connection: Generate Session for accounts: Started')
        user_accounts = AccountKeys.objects.filter(is_active=True)

        for user_account_obj in user_accounts:
            connection = SmartConnect(api_key=user_account_obj.api_key)
            connection.generateSession(user_account_obj.user_id, user_account_obj.user_pin, totp=pyotp.TOTP(user_account_obj.totp_key).now())
            account_connections[user_account_obj.user_id] = connection

            # Get Account Detail
            account_detail = connection.getProfile(connection.refresh_token)
            if account_detail['message'] == 'SUCCESS':
                # Get Funds detail
                if now.time() < time(9, 14, 00):
                    fund_detail = connection.rmsLimit()
                    if fund_detail['message'] == 'SUCCESS':
                        account_config, _ = AccountConfiguration.objects.get_or_create(account=user_account_obj)
                        account_config.account_balance = float(fund_detail['data']['availablecash'])
                        if account_config.total_open_position > account_config.active_open_position:
                            account_config.entry_amount = float(fund_detail['data']['availablecash'])/(account_config.total_open_position-account_config.active_open_position)
                            account_config.save()

                print(f'MoneyBall: Account Connection: Session generated for {account_detail["data"]["name"]} : {account_detail["data"]["clientcode"]}')
            else:
                print(f'MoneyBall: Account Connection: failed to generated session for {user_account_obj.first_name} {user_account_obj.last_name} : {user_account_obj.user_id}')

        print(f'MoneyBall: Account Connection: Generate Session for accounts: Ended')
    except Exception as e:
        print(f'MoneyBall: Account Connection: Error: {e}')
    print(f'MoneyBall: Account Connection: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def BrokerConnection():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:

        print(f'MoneyBall: Awake the Socket Service: Started')
        x = requests.get(f"{SOCKET_STREAM_URL_DOMAIN}/api/system_conf/awake", verify=False)
        print(f'MoneyBall: Awake the Socket Service: Execution Time(hh:mm:ss): {x.status_code} : {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')

        print(f'MoneyBall: Broker Connection: Started')
        global broker_connection
        try:
            broker_connection.terminateSession(BROKER_USER_ID)
            sleep(5)
        except Exception as e:
            print(f'MoneyBall: Broker Connection: Trying to Terminate Session Error: {e}')
        
        broker_connection = SmartConnect(api_key=BROKER_API_KEY)
        broker_connection.generateSession(BROKER_USER_ID, BROKER_PIN, totp=pyotp.TOTP(BROKER_TOTP_KEY).now())
    except Exception as e:
        print(f'MoneyBall: Broker Connection: Error: {e}')
    print(f'MoneyBall: Broker Connection: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def Equity_BreakOut_1(auto_trigger=True):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    product = 'equity'
    log_identifier = 'Equity_BreakOut_1'
    print(f'MoneyBall: {log_identifier}: Runtime : {product} : {now.strftime("%d-%b-%Y %H:%M:%S")}')

    try:
        if auto_trigger:
            if now.time() < time(9, 18, 00):
                raise Exception("Entry Not Started")
            elif now.time() > time(15, 14, 00):
                raise Exception("Entry Not Stopped")

        configuration_obj = Configuration.objects.filter(product=product)[0]

        exclude_symbols_names = Transaction.objects.filter(product=product, indicate='EXIT', created_at__date=now.date(), is_active=True).values_list('name', flat=True)

        symbol_list_1 = Symbol.objects.filter(product=product, nifty100=True, is_active=True).exclude(name__in=exclude_symbols_names).order_by('-volume')
        symbol_list_2 = Symbol.objects.filter(product=product, midcpnifty50=True, is_active=True).exclude(name__in=exclude_symbols_names).order_by('-volume')
        symbol_list_3 = Symbol.objects.filter(product=product, smallcpnifty100=True, is_active=True).exclude(name__in=exclude_symbols_names).order_by('-volume')

        symbol_list = list(symbol_list_1) + list(symbol_list_2) + list(symbol_list_3)

        print(f'MoneyBall: {log_identifier}: Total Equity Symbol Picked: {len(symbol_list)}')

        new_entry = []
        for index, symbol_obj in enumerate(symbol_list):
            try:
                mode = None

                entries_list = StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=True)
                if not entries_list:
                    from_day = now - timedelta(days=365)
                    data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'ONE_DAY', product)
                    sleep(0.3)

                    open = data_frame['Open'].iloc[-1]
                    high = data_frame['High'].iloc[-1]
                    low = data_frame['Low'].iloc[-1]
                    close = data_frame['Close'].iloc[-1]
                    max_high = max(data_frame['High'].iloc[-200:-1])
                    daily_volatility = calculate_volatility(data_frame)

                    # if (symbol_obj.weekhigh52 < close):
                    if (max_high < close):
                        mode = 'CE'

                    else:
                        mode = None

                    if mode not in [None]:
                        data = {
                            'log_identifier': log_identifier,
                            'configuration_obj': configuration_obj,
                            'product': product,
                            'symbol_obj': symbol_obj,
                            'mode': mode,
                            'ltp': close,
                            'target': configuration_obj.target,
                            'stoploss': configuration_obj.stoploss,
                            'fixed_target': configuration_obj.fixed_target,
                            'lot': symbol_obj.lot
                        }
                        new_entry = Price_Action_Trade(data, new_entry)
                else:
                    stock_config_obj = entries_list[0]
                    from_day = now - timedelta(days=100)
                    data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'ONE_DAY', product)
                    sleep(0.3)

                    trsl_ce = min(data_frame['Low'].iloc[-50:-1])

                    if stock_config_obj.mode == 'CE':
                        if not stock_config_obj.tr_hit and (stock_config_obj.stoploss < trsl_ce):
                            stock_config_obj.tr_hit = True
                            stock_config_obj.trailing_sl = trsl_ce
                            print(f'MoneyBall: {log_identifier}: {index+1}: {stock_config_obj.mode} : Stoploss --> Trailing SL : {symbol_obj.symbol}')
                        elif stock_config_obj.tr_hit and (stock_config_obj.trailing_sl < trsl_ce):
                            stock_config_obj.trailing_sl = trsl_ce
                            print(f'MoneyBall: {log_identifier}: {index+1}: {stock_config_obj.mode} : Old Trailing SL --> New Trailing SL : {symbol_obj.symbol}')
                    stock_config_obj.save()
                del mode, entries_list

            except Exception as e:
                StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=False).delete()
                print(f'MoneyBall: {log_identifier}: Error: in Equity-Symbol: {symbol_obj.name} : {e}')
        del symbol_list
        print(f'MoneyBall: {log_identifier}: Total New Entry {len(new_entry)} : New Entries: {new_entry}')

    except Exception as e:
        print(f'MoneyBall: {log_identifier}: ERROR: Main: {e}')
    print(f'MoneyBall: {log_identifier}: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def FnO_BreakOut_1(auto_trigger=True):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    product = 'future'
    log_identifier = 'FnO_BreakOut_1'
    print(f'MoneyBall: {log_identifier}: Runtime : {product} : {now.strftime("%d-%b-%Y %H:%M:%S")}')

    try:
        if auto_trigger:
            if now.time() < time(9, 22, 00):
                raise Exception("Entry Not Started")
            elif now.time() > time(15, 11, 00):
                raise Exception("Entry Not Stopped")

        configuration_obj = Configuration.objects.filter(product=product)[0]
        
        exclude_symbols_names = Transaction.objects.filter(product=product, indicate='ENTRY', created_at__date=now.date(), is_active=True).values_list('name', flat=True)

        symbol_list = Symbol.objects.filter(product='equity', fno=True, is_active=True).exclude(name__in=exclude_symbols_names).order_by('-volume')

        global broker_connection, entry_holder
        if not entry_holder.get(log_identifier):
            entry_holder[log_identifier] = {'Initiated': True}
            print(f'MoneyBall: {log_identifier}: Entry Holder Initiated: {entry_holder.get(log_identifier)}')

        print(f'MoneyBall: {log_identifier}: Total FnO Symbol Picked: {len(symbol_list)} : Entry on hold: {entry_holder[log_identifier]}')

        new_entry = []
        nop = StockConfig.objects.filter(symbol__product=product, is_active=True).count()
        for index, symbol_obj in enumerate(symbol_list):
            try:
                mode = None

                if nop < configuration_obj.open_position:
                    from_day = now - timedelta(days=3)
                    data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'FIVE_MINUTE', product)
                    sleep(0.3)

                    open = data_frame['Open'].iloc[-1]
                    high = data_frame['High'].iloc[-1]
                    low = data_frame['Low'].iloc[-1]
                    close = data_frame['Close'].iloc[-1]
                    prev_close = data_frame['Close'].iloc[-2]

                    max_high = max(data_frame['High'].iloc[-30:-1])
                    min_low = min(data_frame['Low'].iloc[-30:-1])

                    daily_volatility = calculate_volatility(data_frame)

                    super_trend = SUPER_TREND(high=data_frame['High'], low=data_frame['Low'], close=data_frame['Close'], length=10, multiplier=3)
                    bb = BB(data_frame['Close'], timeperiod=15, std_dev=2)

                    entries_list = StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=True)
                    if not entries_list:

                        if close > super_trend.iloc[-1] and prev_close < super_trend.iloc[-2] and high < bb['hband'].iloc[-1] and not ((high > symbol_obj.r1 and low < symbol_obj.r1) or (high > symbol_obj.r2 and low < symbol_obj.r2) or (high > symbol_obj.pivot and low < symbol_obj.pivot) or (high > symbol_obj.s1 and low < symbol_obj.s1) or (high > symbol_obj.s2 and low < symbol_obj.s2)):
                            mode = 'CE'
                            stock_future_symbol = Symbol.objects.filter(
                                                        product='future',
                                                        name=symbol_obj.name,
                                                        symbol__endswith='CE',
                                                        strike__gt=close,
                                                        fno=True,
                                                        is_active=True).order_by('strike')

                        if close < super_trend.iloc[-1] and prev_close > super_trend.iloc[-2] and low > bb['lband'].iloc[-1] and not ((high > symbol_obj.r1 and low < symbol_obj.r1) or (high > symbol_obj.r2 and low < symbol_obj.r2) or (high > symbol_obj.pivot and low < symbol_obj.pivot) or (high > symbol_obj.s1 and low < symbol_obj.s1) or (high > symbol_obj.s2 and low < symbol_obj.s2)):
                            mode = 'PE'
                            stock_future_symbol = Symbol.objects.filter(
                                                        product='future',
                                                        name=symbol_obj.name,
                                                        symbol__endswith='PE',
                                                        strike__lt=close,
                                                        fno=True,
                                                        is_active=True).order_by('-strike')

                        if mode not in [None]:
                            data = {
                                'log_identifier': log_identifier,
                                'configuration_obj': configuration_obj,
                                'product': product,
                                'mode': mode,
                                'target': configuration_obj.target,
                                'stoploss': configuration_obj.stoploss,
                                'fixed_target': configuration_obj.fixed_target,
                            }

                            for fut_sym_obj in stock_future_symbol:
                                ltp = broker_connection.ltpData(fut_sym_obj.exchange, fut_sym_obj.symbol, fut_sym_obj.token)['data']['ltp']
                                lot = fut_sym_obj.lot
                                chk_price = ltp * lot
                                if chk_price < configuration_obj.amount:
                                    while True:
                                        chk_price = ltp * lot
                                        if chk_price >= configuration_obj.amount:
                                            lot = lot - fut_sym_obj.lot
                                            break
                                        lot += fut_sym_obj.lot

                                    data['ltp'] = ltp
                                    data['lot'] = lot
                                    data['symbol_obj'] = fut_sym_obj
                                    new_entry = Price_Action_Trade(data, new_entry)
                                    nop += 1
                                    break
                    else:
                        # Perform action if required for Open Entries
                        pass

                del mode, entries_list

            except Exception as e:
                StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=False).delete()
                print(f'MoneyBall: {log_identifier}: Error: in FnO-Symbol: {symbol_obj.name} : {e}')
        del symbol_list
        print(f'MoneyBall: {log_identifier}: Total New Entry {len(new_entry)} : New Entries: {new_entry} : Entry on hold: {entry_holder[log_identifier]}')

    except Exception as e:
        print(f'MoneyBall: {log_identifier}: ERROR: Main: {e}')
    print(f'MoneyBall: {log_identifier}: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def SquareOff():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'MoneyBall: SQUARE OFF: Runtime : {now.strftime("%d-%b-%Y %H:%M:%S")}')
    try:
        future_configuration_obj = Configuration.objects.filter(product='future')[0]
        equity_configuration_obj = Configuration.objects.filter(product='equity')[0]

        future_entries_list = StockConfig.objects.filter(symbol__product='future', is_active=True)
        equity_intraday_entries_list = StockConfig.objects.filter(symbol__product='equity', mode='PE', is_active=True)

        entries_list = list(future_entries_list) + list(equity_intraday_entries_list)

        print(f'MoneyBall: SQUARE OFF: Loop Started: Total Entries {len(entries_list)}')
        if entries_list:
            for stock_obj in entries_list:
                try:
                    data = {
                        'configuration_obj': future_configuration_obj if stock_obj.symbol.product == 'future' else equity_configuration_obj,
                        'stock_obj': stock_obj
                    }
                    Stock_Square_Off(data, stock_obj.ltp)
                except Exception as e:
                    print(f'MoneyBall: SQUARE OFF: Loop Error: {stock_obj.symbol.symbol} : {stock_obj.mode} : {e}')
        print(f'MoneyBall: SQUARE OFF: Loop Ended')

    except Exception as e:
        print(f'MoneyBall: SQUARE OFF: ERROR: Main:{e}')

    print(f'MoneyBall: SQUARE OFF: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def CheckFnOSymbolDisable():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'MoneyBall: CHECK FNO SYMBOL DISABLE: Runtime : {now.strftime("%d-%b-%Y %H:%M:%S")}')
    try:
        sleep(3)
        fno_entries = StockConfig.objects.filter(symbol__product='future', fno_activation=False)
        global account_connections

        print(f'MoneyBall: CHECK FNO SYMBOL DISABLE: Loop Started: Total Entries {len(fno_entries)}')
        if fno_entries:
            for stock_obj in fno_entries:
                try:
                    account_entry_for_symbol = AccountStockConfig.objects.filter(symbol=stock_obj.symbol.symbol)
                    total_entry_in_accounts = account_entry_for_symbol.count()
                    not_placed_entry = 0
                    if account_entry_for_symbol:
                        for user_stock_config in account_entry_for_symbol:
                            connection = account_connections[user_stock_config.account.user_id]
                            unique_order_id = user_stock_config.order_id.split('@')[0]
                            data = connection.individual_order_details(unique_order_id)
                            if data['data']['orderstatus'] in ['rejected']:
                                AccountTransaction.objects.filter(order_id=user_stock_config.order_id).delete()
                                user_stock_config.delete()
                                not_placed_entry += 1
                        
                        if not_placed_entry == total_entry_in_accounts:
                            print(f'MoneyBall: CHECK FNO SYMBOL DISABLE: Disabling the Symbol {stock_obj.symbol.symbol}')
                            StockConfig.objects.filter(symbol=stock_obj.symbol, fixed_target=stock_obj.fixed_target).delete()
                            Transaction.objects.filter(symbol=stock_obj.symbol.symbol, fixed_target=stock_obj.fixed_target).delete()
                            Symbol.objects.filter(name=stock_obj.symbol.name).update(fno=False)
                        else:
                            stock_obj.fno_activation = True
                            stock_obj.save()
                except Exception as e:
                    print(f'MoneyBall: CHECK FNO SYMBOL DISABLE: Loop Error: {stock_obj.symbol.symbol} : {stock_obj.mode} : {e}')
        print(f'MoneyBall: CHECK FNO SYMBOL DISABLE: Loop Ended')

    except Exception as e:
        print(f'MoneyBall: CHECK FNO SYMBOL DISABLE: ERROR: Main:{e}')

    print(f'MoneyBall: CHECK FNO SYMBOL DISABLE: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def PivotUpdate():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    product = 'equity'
    print(f'MoneyBall: PIVOT UPDATE: Runtime : {now.strftime("%d-%b-%Y %H:%M:%S")}')
    try:
        # Set Pivot Points
        symbol_list = Symbol.objects.filter(product=product, is_active=True).order_by('-fno')

        from_day = now - timedelta(days=5)
        print(f'MoneyBall: PIVOT UPDATE: Started : Total : {symbol_list.count()}')
        for symbol_obj in symbol_list:
            try:
                data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'ONE_DAY', product)
                sleep(0.3)

                last_day = data_frame.iloc[-2]

                pivot_traditional = PIVOT(last_day)
                symbol_obj.pivot = round(pivot_traditional['pivot'], 2)
                symbol_obj.r1 = round(pivot_traditional['r1'], 2)
                symbol_obj.s1 = round(pivot_traditional['s1'], 2)
                symbol_obj.r2 = round(pivot_traditional['r2'], 2)
                symbol_obj.s2 = round(pivot_traditional['s2'], 2)
                symbol_obj.r3 = round(pivot_traditional['r3'], 2)
                symbol_obj.s3 = round(pivot_traditional['s3'], 2)

                symbol_obj.save()
                print(f'MoneyBall: PIVOT UPDATE: Updated: {symbol_obj.name}')
            except Exception as e:
                print(f'MoneyBall: PIVOT UPDATE: Loop Error: {str(e)}')
        print(f'MoneyBall: PIVOT UPDATE: Ended')
    except Exception as e:
        print(f'MoneyBall: PIVOT UPDATE: Error: {str(e)}')
    print(f'MoneyBall: PIVOT UPDATE: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True
