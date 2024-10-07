from time import sleep
from django.db import transaction
from stock.models import Transaction
from django.dispatch import receiver
from helper.angel_order import Create_Order
from django.db.models.signals import post_save
from moneyball.settings import account_connections
from account.models import AccountConfiguration, AccountStockConfig, AccountTransaction


def AccountExitAction(instance):
    try:
        global account_connections
        print(f"MoneyBall: Account Exit Action {instance.get('indicate')}")
        # Fetch Active User
        user_account_stock_configs = AccountStockConfig.objects.filter(
                                                        product=instance.get('product'),
                                                        symbol=instance.get('symbol'),
                                                        name=instance.get('name'),
                                                        mode=instance.get('mode'),
                                                        is_active=True)
        if user_account_stock_configs:
            print(f"MoneyBall: Account Exit Action {instance.get('indicate')}: Total Users for Exit: {user_account_stock_configs.count()}")

            for user_stock_config in user_account_stock_configs:
                try:
                    print(f"MoneyBall: Account Exit Action {instance.get('indicate')}: User: {user_stock_config.account.first_name} {user_stock_config.account.last_name} - {user_stock_config.account.user_id} : {instance.get('product')} : {instance.get('symbol')}")
                    
                    # get user connection
                    connection = account_connections[user_stock_config.account.user_id]

                    # Place Order
                    if instance.get('product') == 'future':
                        order_id, order_status = Create_Order(connection, 'SELL', 'CARRYFORWARD', instance.get('token'), instance.get('symbol'), instance.get('exchange'), instance.get('price'), user_stock_config.lot, "MARKET")
                    else:
                        if instance.get('mode') == 'CE':
                            order_id, order_status = Create_Order(connection, 'SELL', 'DELIVERY', instance.get('token'), instance.get('symbol'), instance.get('exchange'), instance.get('price'), user_stock_config.lot, "MARKET")
                        else:
                            order_id, order_status = Create_Order(connection, 'BUY', 'INTRADAY', instance.get('token'), instance.get('symbol'), instance.get('exchange'), instance.get('price'), user_stock_config.lot, "MARKET")
                    
                    # print(f"MoneyBall: Account Exit Action {instance.get('indicate')}: User: {user_stock_config.account.first_name} {user_stock_config.account.last_name} - {user_stock_config.account.user_id} : {instance.get('product')} : {instance.get('symbol')} : {order_id} : {order_status} : Lots : {user_stock_config.lot}")

                    if order_id not in ['0', 0, None]:
                        AccountTransaction.objects.create(
                                                account=user_stock_config.account,
                                                product=instance.get('product'),
                                                symbol=instance.get('symbol'),
                                                name=instance.get('name'),
                                                exchange=instance.get('exchange'),
                                                mode=instance.get('mode'),
                                                indicate=instance.get('indicate'),
                                                type=instance.get('type'),
                                                price=instance.get('price'),
                                                target=instance.get('target'),
                                                fixed_target=instance.get('fixed_target'),
                                                stoploss=instance.get('stoploss'),
                                                profit=instance.get('profit'),
                                                max=instance.get('max'),
                                                max_l=instance.get('max_l'),
                                                highest_price=instance.get('highest_price'),
                                                order_id=order_id,
                                                order_status=order_status,
                                                lot=user_stock_config.lot)
                        user_stock_config.delete()
                        if instance.get('product') == 'equity':
                            if instance.get('mode') == 'CE':
                                user_config = AccountConfiguration.objects.get(account=user_stock_config.account, is_active=True)
                                user_config.active_open_position -= 1
                                user_config.save()
                
                except Exception as e:
                    print(f"MoneyBall: Account Exit Action {instance.get('indicate')}: User Loop Error: {e}")
        else:
            print(f"MoneyBall: Account Exit Action {instance.get('indicate')}: No User for Exit: {user_account_stock_configs.count()}")
    except Exception as e:
        print(f"MoneyBall: Account Exit Action Main: Error: {e}")
    return True



def AccountEntryAction(sender, instance, created):
    try:
        global account_connections
        print(f"MoneyBall: Account Entry Action {instance.indicate} : {instance.product} : {instance.symbol}")
        if instance.indicate == 'ENTRY':

            # Fetch Active User
            user_account_configs = AccountConfiguration.objects.filter(place_order=True, account__is_active=True)

            if user_account_configs:
                print(f"MoneyBall: Account Entry Action {instance.indicate}: Total User for Entry: {user_account_configs.count()}")

                for user_config in user_account_configs:
                    try:
                        order_id = None
                        print(f"MoneyBall: Account Entry Action {instance.indicate}: User: {user_config.account.first_name} {user_config.account.last_name} - {user_config.account.user_id} : {instance.product} : {instance.symbol}")
                        # get user connection
                        connection = account_connections[user_config.account.user_id]

                        # Place Order
                        if instance.price < user_config.entry_amount and user_config.total_open_position > user_config.active_open_position:
                            lot = instance.lot
                            if instance.product == 'future':
                                order_id, order_status = Create_Order(connection, 'BUY', 'CARRYFORWARD', instance.token, instance.symbol, instance.exchange, instance.price, lot, "MARKET")
                            else:
                                chk_price = instance.price * lot
                                if chk_price < user_config.entry_amount:
                                    while True:
                                        chk_price = instance.price * lot
                                        if chk_price >= user_config.entry_amount:
                                            lot = lot - instance.lot
                                            break
                                        lot += instance.lot
                                if instance.mode == 'CE':
                                    order_id, order_status = Create_Order(connection, 'BUY', 'DELIVERY', instance.token, instance.symbol, instance.exchange, instance.price, lot, "LIMIT")
                                else:
                                    order_id, order_status = Create_Order(connection, 'SELL', 'INTRADAY', instance.token, instance.symbol, instance.exchange, instance.price, lot, "LIMIT")

                            # print(f"MoneyBall: Account Entry Action {instance.indicate}: User: {user_config.account.first_name} {user_config.account.last_name} - {user_config.account.user_id} : {instance.product} : {instance.symbol} : {order_id} : {order_status} : Lots : {lot}")

                            if order_id not in ['0', 0, None]:
                                account_stock_config_obj, created = AccountStockConfig.objects.get_or_create(
                                                                            account=user_config.account,
                                                                            product=instance.product,
                                                                            symbol=instance.symbol,
                                                                            name=instance.name,
                                                                            mode=instance.mode,
                                                                            is_active=True)
                                account_stock_config_obj.lot = lot
                                account_stock_config_obj.order_id = order_id
                                account_stock_config_obj.order_status = order_status
                                account_stock_config_obj.save()

                                AccountTransaction.objects.create(
                                                        account=user_config.account,
                                                        product=instance.product,
                                                        symbol=instance.symbol,
                                                        name=instance.name,
                                                        exchange=instance.exchange,
                                                        mode=instance.mode,
                                                        indicate=instance.indicate,
                                                        type=instance.type,
                                                        price=instance.price,
                                                        target=instance.target,
                                                        fixed_target=instance.fixed_target,
                                                        stoploss=instance.stoploss,
                                                        order_id=order_id,
                                                        order_status=order_status,
                                                        lot=lot)
                                if instance.product == 'equity':
                                    if instance.mode == 'CE':
                                        user_config.active_open_position += 1
                                        user_config.save()
                        else:
                            print(f"MoneyBall: Account Entry Action {instance.indicate}: User may have Max Active Open posotion : Total - {user_config.total_open_position}, Active - {user_config.active_open_position}")
                            print(f"MoneyBall: Account Entry Action {instance.indicate}: User may not have enough money to by a single share : 1 Share Price {instance.price}, - User Entry Amount {user_config.entry_amount}")
                    
                    except Exception as e:
                        print(f"MoneyBall: Account Entry Action {instance.indicate}: User Loop Error: {e}")
            else:
                print(f"MoneyBall: Account Entry Action {instance.indicate}: No User for Entry: {user_account_configs.count()}")
        else:
            print(f"MoneyBall: Account Entry Action: Not allowed on transaction indicator : {instance.indicate}")
    except Exception as e:
        print(f"MoneyBall: Account Entry Action Main: Error: {e}")
    return True


@receiver(post_save, sender=Transaction)
def OnAlgoTransaction(sender, instance, created, **kwargs):
  if created:
    sleep(1)
    transaction.on_commit(lambda: AccountEntryAction(sender, instance, created))