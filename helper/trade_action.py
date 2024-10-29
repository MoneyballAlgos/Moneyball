
import requests
from stock.models import StockConfig, Transaction
from moneyball.settings import SOCKET_STREAM_URL_DOMAIN
from helper.common import next_multiple_of_5_after_decimal

def Price_Action_Trade(data, new_entry):
    price = next_multiple_of_5_after_decimal(data['ltp'])
    if price == 0:
        return new_entry
    stock_config_obj, created = StockConfig.objects.get_or_create(mode=data['mode'], symbol=data['symbol_obj'], is_active=False)
    if created:
        stock_config_obj.lot = data['lot']
        stock_config_obj.price = price
        stock_config_obj.highest_price = price
        stock_config_obj.stoploss = next_multiple_of_5_after_decimal(round(price - price * (data['stoploss'])/100, len(str(price).split('.')[-1])))
        stock_config_obj.target = next_multiple_of_5_after_decimal(round(price + price * (data['target'])/100, len(str(price).split('.')[-1])))
        stock_config_obj.fixed_target = next_multiple_of_5_after_decimal(round(price + price * (data['fixed_target'])/100, len(str(price).split('.')[-1])))
        stock_config_obj.is_active = True
        stock_config_obj.trailing_sl = 0

        stock_config_obj.save()
        # TRANSACTION TABLE UPDATE
        Transaction.objects.create(
                                    product=data['symbol_obj'].product,
                                    symbol=data['symbol_obj'].symbol,
                                    name=data['symbol_obj'].name,
                                    token=data['symbol_obj'].token,
                                    exchange=data['symbol_obj'].exchange,
                                    mode=data['mode'],
                                    indicate='ENTRY',
                                    type='LONG' if data['mode'] == 'CE' else 'SHORT',
                                    price=price,
                                    target=stock_config_obj.target,
                                    fixed_target=stock_config_obj.fixed_target,
                                    stoploss=stock_config_obj.stoploss,
                                    lot=stock_config_obj.lot)
        print(f'MoneyBall: {data["log_identifier"]}: Entry on {data["product"]} : {data["symbol_obj"].name} on {price}')
        new_entry.append((data["symbol_obj"].exchange, data["symbol_obj"].name, data["symbol_obj"].token))

        # Start Socket Streaming
        correlation_id = "moneyball-socket"
        socket_mode = 1
        nse = []
        nfo = []
        bse = []
        bfo = []
        mcx = []

        if data["symbol_obj"].exchange == 'NSE':
            nse.append(data["symbol_obj"].token)
        elif data["symbol_obj"].exchange == 'NFO':
            nfo.append(data["symbol_obj"].token)
        elif data["symbol_obj"].exchange == 'BSE':
            bse.append(data["symbol_obj"].token)
        elif data["symbol_obj"].exchange == 'BFO':
            bfo.append(data["symbol_obj"].token)
        else:
            mcx.append(data["symbol_obj"].token)

        subscribe_list = []
        for index, i in enumerate((nse,nfo,bse,bfo,mcx)):
            if i:
                subscribe_list.append({
                    "exchangeType": index+1,
                    "tokens": i
                })
        url = f"{SOCKET_STREAM_URL_DOMAIN}/api/system_conf/socket-stream/"
        data_json = {
            "subscribe_list": subscribe_list,
            "correlation_id": correlation_id,
            "socket_mode": socket_mode
        }
        response = requests.post(url, json=data_json, verify=False)
        print(f'MoneyBall: {data["log_identifier"]}: New Entries: {url} : Streaming Response: {response.status_code}')
    return new_entry


def Stock_Square_Off(data, ltp):
    # Exit Order.
    price = ltp
    diff = (price - data['stock_obj'].price)
    profit = round((((diff/data['stock_obj'].price) * 100)), 2)
    # TRANSACTION TABLE UPDATE
    Transaction.objects.create(
                            product=data['stock_obj'].symbol.product,
                            mode=data['stock_obj'].mode,
                            symbol=data['stock_obj'].symbol.symbol,
                            name=data['stock_obj'].symbol.name,
                            token=data['stock_obj'].symbol.token,
                            exchange=data['stock_obj'].symbol.exchange,
                            indicate='EXIT',
                            type=data['exit_type'],
                            price=price,
                            target=data['stock_obj'].target,
                            stoploss=data['stock_obj'].stoploss,
                            profit=profit,
                            max=data['stock_obj'].max,
                            max_l=data['stock_obj'].max_l,
                            highest_price=data['stock_obj'].highest_price,
                            fixed_target=data['stock_obj'].fixed_target,
                            lot=data['stock_obj'].lot)
    print(f"MoneyBall: SQUARE OFF EXIT: Unsubscribed : {data['stock_obj'].symbol.symbol} : {data['stock_obj'].symbol.token}")
    data['stock_obj'].delete()
    return True
