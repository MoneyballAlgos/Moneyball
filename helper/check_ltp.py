import requests
from stock.models import Transaction
from moneyball.settings import BED_URL_DOMAIN


def TrailingTargetUpdate(data, ltp):
    # TARGET Exit
    if (ltp >= data['stock_obj'].target):
        data['stock_obj'].tr_hit = True
        data['stock_obj'].target =  round(ltp + ltp * data['target'], len(str(ltp).split('.')[-1]))
        data['stock_obj'].trailing_sl = round(ltp - ltp * data['stoploss'], len(str(ltp).split('.')[-1]))
        data['stock_obj'].save()
        return True
    return False


def TargetExit(data, ltp, open_position, correlation_id, socket_mode, sws):
    # TARGET Exit
    if (ltp >= data['stock_obj'].fixed_target):
        # Exit Order.

        price = ltp
        del open_position[data['stock_obj'].symbol.token]
        diff = (price - data['stock_obj'].price)
        profit = round((((diff/data['stock_obj'].price) * 100)), 2)
        # TRANSACTION TABLE UPDATE
        transaction_obj, _ = Transaction.objects.get_or_create(
                                product=data['stock_obj'].symbol.product,
                                mode=data['stock_obj'].mode,
                                symbol=data['stock_obj'].symbol.symbol,
                                name=data['stock_obj'].symbol.name,
                                token=data['stock_obj'].symbol.token,
                                exchange=data['stock_obj'].symbol.exchange,
                                indicate='EXIT',
                                type='TARGET',
                                price=price,
                                target=data['stock_obj'].target,
                                stoploss=data['stock_obj'].stoploss,
                                profit=profit,
                                max=data['stock_obj'].max,
                                max_l=data['stock_obj'].max_l,
                                highest_price=data['stock_obj'].highest_price,
                                fixed_target=data['stock_obj'].fixed_target,
                                lot=data['stock_obj'].lot)
        sws.unsubscribe(correlation_id, socket_mode, [{"action": 0, "exchangeType": 1, "tokens": [data['stock_obj'].symbol.token]}])
        print(f"MoneyBall: TARGET EXIT: Unsubscribed : {data['stock_obj'].symbol.symbol} : {data['stock_obj'].symbol.token}")
        data['stock_obj'].delete()
        print(f"MoneyBall: TARGET EXIT: Exit from all accounts: Api Calling")
        transaction_data = {
            'product': transaction_obj.product,
            'mode': transaction_obj.mode,
            'symbol': transaction_obj.symbol,
            'name': transaction_obj.name,
            'token': transaction_obj.token,
            'exchange': transaction_obj.exchange,
            'indicate': transaction_obj.indicate,
            'type': transaction_obj.type,
            'price': transaction_obj.price,
            'target': transaction_obj.target,
            'stoploss': transaction_obj.stoploss,
            'profit': transaction_obj.profit,
            'max': transaction_obj.max,
            'max_l': transaction_obj.max_l,
            'highest_price': transaction_obj.highest_price,
            'fixed_target': transaction_obj.fixed_target,
            'lot': transaction_obj.lot
        }
        x = requests.post(f"{BED_URL_DOMAIN}/api/account/exit-transaction", json=transaction_data, verify=False)
        print(f"MoneyBall: TARGET EXIT: Exit from all accounts: Api Called: {x.status_code}")
    return True


def TrailingStopLossExit(data, ltp, open_position, correlation_id, socket_mode, sws):
    # StopLoss and Trailing StopLoss Exit
    price_value, exit_type = (data['stock_obj'].trailing_sl, 'TR-SL') if data['stock_obj'].tr_hit else (data['stock_obj'].stoploss, 'STOPLOSS')
    if (ltp <= price_value):
        # Exit Order.

        del open_position[data['stock_obj'].symbol.token]
        # diff = (price - data['stock_obj'].price)
        diff = (price_value - data['stock_obj'].price)
        profit = round((((diff/data['stock_obj'].price) * 100)), 2)
        # TRANSACTION TABLE UPDATE
        transaction_obj, _ = Transaction.objects.get_or_create(
                                product=data['stock_obj'].symbol.product,
                                mode=data['stock_obj'].mode,
                                symbol=data['stock_obj'].symbol.symbol,
                                name=data['stock_obj'].symbol.name,
                                token=data['stock_obj'].symbol.token,
                                exchange=data['stock_obj'].symbol.exchange,
                                indicate='EXIT',
                                type=exit_type,
                                price=price_value,
                                target=data['stock_obj'].target,
                                stoploss=data['stock_obj'].stoploss,
                                profit=profit,
                                max=data['stock_obj'].max,
                                max_l=data['stock_obj'].max_l,
                                highest_price=data['stock_obj'].highest_price,
                                fixed_target=data['stock_obj'].fixed_target,
                                lot=data['stock_obj'].lot)
        sws.unsubscribe(correlation_id, socket_mode, [{"action": 0, "exchangeType": 1, "tokens": [data['stock_obj'].symbol.token]}])
        print(f"MoneyBall: TRAILING/STOPLOSS EXIT: Unsubscribed : {data['stock_obj'].symbol.symbol} : {data['stock_obj'].symbol.token}")
        data['stock_obj'].delete()
        print(f"MoneyBall: TRAILING/STOPLOSS EXIT: Exit from all accounts: Api Calling")
        transaction_data = {
            'product': transaction_obj.product,
            'mode': transaction_obj.mode,
            'symbol': transaction_obj.symbol,
            'name': transaction_obj.name,
            'token': transaction_obj.token,
            'exchange': transaction_obj.exchange,
            'indicate': transaction_obj.indicate,
            'type': transaction_obj.type,
            'price': transaction_obj.price,
            'target': transaction_obj.target,
            'stoploss': transaction_obj.stoploss,
            'profit': transaction_obj.profit,
            'max': transaction_obj.max,
            'max_l': transaction_obj.max_l,
            'highest_price': transaction_obj.highest_price,
            'fixed_target': transaction_obj.fixed_target,
            'lot': transaction_obj.lot
        }
        x = requests.post(f"{BED_URL_DOMAIN}/api/account/exit-transaction", json=transaction_data, verify=False)
        print(f"MoneyBall: TRAILING/STOPLOSS EXIT: Exit from all accounts: Api Called: {x.status_code}")
    return False
