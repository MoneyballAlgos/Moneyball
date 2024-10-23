import threading
from time import sleep
from django.db import transaction
from helper.emails import email_send
from django.dispatch import receiver
from system_conf.models import Symbol
from django.db.models.signals import post_save
from stock.models import StockConfig, Transaction
from moneyball.settings import account_connections
from helper.angel_order import Cancel_Order, Create_Order, Is_Order_Completed
from account.models import AccountConfiguration, AccountStockConfig, AccountTransaction
from helper.response_message import ENTRY_ORDER_FAILED, ENTRY_ORDER_PLACED, STOPLOSS_ORDER_PLACED, TARGET_ORDER_PLACED, TRSL_ORDER_PLACED


def AccountExitAction(instance):
    try:
        global account_connections
        print(f"MoneyBall: Account Trade Action {instance.get('indicate')}")
        # Fetch Active User
        user_account_stock_configs = AccountStockConfig.objects.filter(
                                                        product=instance.get('product'),
                                                        symbol=instance.get('symbol'),
                                                        name=instance.get('name'),
                                                        mode=instance.get('mode'),
                                                        is_active=True)
        if user_account_stock_configs:
            print(f"MoneyBall: Account Trade Action {instance.get('indicate')}: Total Users for Exit: {user_account_stock_configs.count()}")

            for user_stock_config in user_account_stock_configs:
                try:
                    print(f"MoneyBall: Account Trade Action {instance.get('indicate')}: User: {user_stock_config.account.first_name} {user_stock_config.account.last_name} - {user_stock_config.account.user_id} : {instance.get('product')} : {instance.get('symbol')}")
                    
                    # get user connection
                    connection = account_connections[user_stock_config.account.user_id]

                    # Place Order
                    # Future CE and PE
                    if instance.get('product') == 'future':
                        if user_stock_config.order_placed or Is_Order_Completed(connection, user_stock_config.order_id):
                            order_id, order_status = user_stock_config.order_id, user_stock_config.order_status
                            if instance.get('type') == 'STOPLOSS':
                                if not user_stock_config.stoploss_order_placed:
                                    order_id, order_status = Create_Order(connection, 'SELL', 'CARRYFORWARD', instance.get('token'), instance.get('symbol'), instance.get('exchange'), instance.get('price'), user_stock_config.lot, "LIMIT")
                                email_message = STOPLOSS_ORDER_PLACED.format(symbol=instance.get('symbol'), price=instance.get('price'), profit=instance.get('profit'), order_id=order_id)
                                
                                # Send Email Notification
                                subject = f"Fno Trade on {instance.get('symbol')}" if instance.get('product') == 'future' else f"Equity Trade on {instance.get('name')}"
                                template = 'stoploss_hit.html'
                                recipients = [user_stock_config.account.email]
                                email_context = {
                                    'name': user_stock_config.account.first_name,
                                    "symbol": instance.get('symbol'),
                                    "price": instance.get('price'),
                                    "profit": instance.get('profit'),
                                    "order_id": order_id
                                }
                                email_send(subject, template, recipients, email_context)
                            elif instance.get('type') == 'TARGET':
                                if not user_stock_config.target_order_placed:
                                    order_id, order_status = Create_Order(connection, 'SELL', 'CARRYFORWARD', instance.get('token'), instance.get('symbol'), instance.get('exchange'), instance.get('price'), user_stock_config.lot, "LIMIT")
                                email_message = TARGET_ORDER_PLACED.format(symbol=instance.get('symbol'), price=instance.get('price'), profit=instance.get('profit'), order_id=order_id)

                                # Send Email Notification
                                subject = f"Fno Trade on {instance.get('symbol')}" if instance.get('product') == 'future' else f"Equity Trade on {instance.get('name')}"
                                template = 'target_hit.html'
                                recipients = [user_stock_config.account.email]
                                email_context = {
                                    'name': user_stock_config.account.first_name,
                                    "symbol": instance.get('symbol'),
                                    "price": instance.get('price'),
                                    "profit": instance.get('profit'),
                                    "order_id": order_id
                                }
                                email_send(subject, template, recipients, email_context)
                            elif instance.get('type') in ['TR-SL', 'SQ-OFF', 'PIVOT']:
                                if user_stock_config.stoploss_order_placed:
                                    _, _ = Cancel_Order(connection, user_stock_config.stoploss_order_id)
                                if user_stock_config.target_order_placed:
                                    _, _ = Cancel_Order(connection, user_stock_config.target_order_id)
                                
                                order_id, order_status = Create_Order(connection, 'SELL', 'CARRYFORWARD', instance.get('token'), instance.get('symbol'), instance.get('exchange'), instance.get('price'), user_stock_config.lot, "LIMIT")
                                
                                email_message = TRSL_ORDER_PLACED.format(symbol=instance.get('symbol'), price=instance.get('price'), profit=instance.get('profit'), order_id=order_id)

                                # Send Email Notification
                                subject = f"Fno Trade on {instance.get('symbol')}" if instance.get('product') == 'future' else f"Equity Trade on {instance.get('name')}"
                                template = 'tr_sl_hit.html'
                                recipients = [user_stock_config.account.email]
                                email_context = {
                                    'name': user_stock_config.account.first_name,
                                    "symbol": instance.get('symbol'),
                                    "price": instance.get('price'),
                                    "profit": instance.get('profit'),
                                    "order_id": order_id
                                }
                                email_send(subject, template, recipients, email_context)
                        else:
                            order_id, order_status = Cancel_Order(connection, user_stock_config.order_id)
                    # Equity Delivery and INTRADAY(PE)
                    else:
                        # Equity Delivery
                        if instance.get('mode') == 'CE':
                            order_id, order_status = Create_Order(connection, 'SELL', 'DELIVERY', instance.get('token'), instance.get('symbol'), instance.get('exchange'), instance.get('price'), user_stock_config.lot, "MARKET")
                        # Equity INTRADAY(PE)
                        else:
                            if user_stock_config.order_placed or Is_Order_Completed(connection, user_stock_config.order_id):
                                order_id, order_status = user_stock_config.order_id, user_stock_config.order_status
                                if instance.get('type') == 'STOPLOSS':
                                    if not user_stock_config.stoploss_order_placed:
                                        order_id, order_status = Create_Order(connection, 'BUY', 'INTRADAY', instance.get('token'), instance.get('symbol'), instance.get('exchange'), instance.get('price'), user_stock_config.lot, "MARKET")
                                elif instance.get('type') == 'TARGET':
                                    if not user_stock_config.target_order_placed:
                                        order_id, order_status = Create_Order(connection, 'BUY', 'INTRADAY', instance.get('token'), instance.get('symbol'), instance.get('exchange'), instance.get('price'), user_stock_config.lot, "MARKET")
                                elif instance.get('type') in ['TR-SL', 'SQ-OFF', 'PIVOT']:
                                    if user_stock_config.stoploss_order_placed:
                                        _, _ = Cancel_Order(connection, user_stock_config.stoploss_order_id)
                                    if user_stock_config.target_order_placed:
                                        _, _ = Cancel_Order(connection, user_stock_config.target_order_id)

                                    order_id, order_status = Create_Order(connection, 'BUY', 'INTRADAY', instance.get('token'), instance.get('symbol'), instance.get('exchange'), instance.get('price'), user_stock_config.lot, "MARKET")
                            else:
                                order_id, order_status = Cancel_Order(connection, user_stock_config.order_id)
                    
                    # print(f"MoneyBall: Account Trade Action {instance.get('indicate')}: User: {user_stock_config.account.first_name} {user_stock_config.account.last_name} - {user_stock_config.account.user_id} : {instance.get('product')} : {instance.get('symbol')} : {order_id} : {order_status} : Lots : {user_stock_config.lot}")

                    if order_id not in ['0', 0, None]:
                        AccountTransaction.objects.create(
                                                account=user_stock_config.account,
                                                product=instance.get('product'),
                                                symbol=instance.get('symbol'),
                                                name=instance.get('name'),
                                                token=instance.get('token'),
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
                    print(f"MoneyBall: Account Trade Action {instance.get('indicate')}: User Loop Error: {e}")
        else:
            print(f"MoneyBall: Account Trade Action {instance.get('indicate')}: No User for Exit: {user_account_stock_configs.count()}")
    except Exception as e:
        print(f"MoneyBall: Account Trade Action Main: Error Exit Func: {e}")
    return True


def UserTrade(sender, instance, created, user_config):
    global account_connections
    order_id = None
    print(f"MoneyBall: Account Trade Action {instance.indicate}: User: {user_config.account.first_name} {user_config.account.last_name} - {user_config.account.user_id} : {instance.product} : {instance.symbol}")
    # get user connection
    connection = account_connections[user_config.account.user_id]

    # Place Order
    if user_config.total_open_position > user_config.active_open_position:
        lot = instance.lot
        
        # Future CE and PE
        if instance.product == 'future':
            order_id, order_status = Create_Order(connection, 'BUY', 'CARRYFORWARD', instance.token, instance.symbol, instance.exchange, instance.price, lot, "LIMIT")

        # Equity Delivery and INTRADAY(PE)
        else:
            chk_price = instance.price * lot
            if chk_price < user_config.entry_amount:
                while True:
                    chk_price = instance.price * lot
                    if chk_price >= user_config.entry_amount:
                        lot = lot - instance.lot
                        break
                    lot += instance.lot
            
            # Equity Delivery
            if instance.mode == 'CE':
                order_id, order_status = Create_Order(connection, 'BUY', 'DELIVERY', instance.token, instance.symbol, instance.exchange, instance.price, lot, "LIMIT")
            
            # Equity INTRADAY(PE)
            else:
                order_id, order_status = Create_Order(connection, 'SELL', 'INTRADAY', instance.token, instance.symbol, instance.exchange, instance.price, lot, "LIMIT")

        # print(f"MoneyBall: Account Trade Action {instance.indicate}: User: {user_config.account.first_name} {user_config.account.last_name} - {user_config.account.user_id} : {instance.product} : {instance.symbol} : {order_id} : {order_status} : Lots : {lot}")

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
                                    token=instance.token,
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

            # Send Email Notification
            subject = f"Fno Trade on {instance.symbol}" if instance.product == 'future' else f"Equity Trade on {instance.name}"
            template = 'order_placed.html'
            recipients = [user_config.account.email]
            email_context = {
                'name': user_config.account.first_name,
                "symbol": instance.symbol,
                "price": round(instance.price, 2),
                "target": instance.fixed_target,
                "stoploss": instance.stoploss,
                "order_id": order_id
            }
            email_send(subject, template, recipients, email_context)
    else:
        print(f"MoneyBall: Account Trade Action {instance.indicate}: User may have Max Active Open posotion : Total - {user_config.total_open_position}, Active - {user_config.active_open_position}")
        print(f"MoneyBall: Account Trade Action {instance.indicate}: User may not have enough money to by a single share : 1 Share Price {instance.price}, - User Entry Amount {user_config.entry_amount}")
    return True



def AccountTradeAction(sender, instance, created):
    try:
        print(f"MoneyBall: Account Trade Action {instance.indicate} : {instance.product} : {instance.symbol}")
        if instance.indicate == 'ENTRY':
            symbol_obj = Symbol.objects.get(token=instance.token, is_active=True)

            # Fetch Active User
            if instance.product == 'equity':
                user_accounts = []
                if symbol_obj.nifty50:
                    user_accounts.extend(list(AccountConfiguration.objects.filter(place_order=True, equity_enabled=True, nifty50=True, entry_amount__gte=instance.price, account__is_active=True)))
                if symbol_obj.nifty100:
                    user_accounts.extend(list(AccountConfiguration.objects.filter(place_order=True, equity_enabled=True, nifty100=True, entry_amount__gte=instance.price, account__is_active=True)))
                if symbol_obj.nifty200:
                    user_accounts.extend(list(AccountConfiguration.objects.filter(place_order=True, equity_enabled=True, nifty200=True, entry_amount__gte=instance.price, account__is_active=True)))
                if symbol_obj.midcpnifty50:
                    user_accounts.extend(list(AccountConfiguration.objects.filter(place_order=True, equity_enabled=True, midcpnifty50=True, entry_amount__gte=instance.price, account__is_active=True)))
                if symbol_obj.midcpnifty100:
                    user_accounts.extend(list(AccountConfiguration.objects.filter(place_order=True, equity_enabled=True, midcpnifty100=True, entry_amount__gte=instance.price, account__is_active=True)))
                if symbol_obj.midcpnifty150:
                    user_accounts.extend(list(AccountConfiguration.objects.filter(place_order=True, equity_enabled=True, midcpnifty150=True, entry_amount__gte=instance.price, account__is_active=True)))
                if symbol_obj.smallcpnifty50:
                    user_accounts.extend(list(AccountConfiguration.objects.filter(place_order=True, equity_enabled=True, smallcpnifty50=True, entry_amount__gte=instance.price, account__is_active=True)))
                if symbol_obj.smallcpnifty100:
                    user_accounts.extend(list(AccountConfiguration.objects.filter(place_order=True, equity_enabled=True, smallcpnifty100=True, entry_amount__gte=instance.price, account__is_active=True)))
                if symbol_obj.smallcpnifty250:
                    user_accounts.extend(list(AccountConfiguration.objects.filter(place_order=True, equity_enabled=True, smallcpnifty250=True, entry_amount__gte=instance.price, account__is_active=True)))
                
                temp_user_account_ids = []
                user_account_configs = []
                for user_obj in user_accounts:
                    if user_obj.account.user_id not in temp_user_account_ids:
                        temp_user_account_ids.append(user_obj.account.user_id)
                        user_account_configs.append(user_obj)
                
            else:
                user_account_configs = AccountConfiguration.objects.filter(place_order=True, fno_enabled=True, account__is_active=True)

            if user_account_configs:
                print(f"MoneyBall: Account Trade Action {instance.indicate}: Total User for Entry: {len(user_account_configs)}")

                for user_config in user_account_configs:
                    try:
                        # Open threads for user
                        user_thread = threading.Thread(name=f"User-{instance.symbol}-{user_config.account.first_name}", target=UserTrade, args=(sender, instance, created, user_config), daemon=True)
                        user_thread.start()

                    except Exception as e:
                        print(f"MoneyBall: Account Trade Action {instance.indicate}: User Loop Error: {e}")
            else:
                print(f"MoneyBall: Account Trade Action {instance.indicate}: No User for Entry: {len(user_account_configs)}")
        elif instance.indicate == 'EXIT':
            transaction_data = {
                'product': instance.product,
                'mode': instance.mode,
                'symbol': instance.symbol,
                'name': instance.name,
                'token': instance.token,
                'exchange': instance.exchange,
                'indicate': instance.indicate,
                'type': instance.type,
                'price': instance.price,
                'target': instance.target,
                'stoploss': instance.stoploss,
                'profit': instance.profit,
                'max': instance.max,
                'max_l': instance.max_l,
                'highest_price': instance.highest_price,
                'fixed_target': instance.fixed_target,
                'lot': instance.lot
            }
            AccountExitAction(transaction_data)
        else:
            print(f"MoneyBall: Account Trade Action: Not allowed on transaction indicator : {instance.indicate}")
    except Exception as e:
        print(f"MoneyBall: Account Trade Action Main: Error Trade Func: {e}")
    return True


def AccountPlaceTargetStoplossOrder(sender, instance, created):
    try:
        sleep(3)
        global account_connections

        # get user connection
        connection = account_connections[instance.account.user_id]

        print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} {instance.indicate} : {instance.product} : {instance.symbol}")
        if instance.indicate == 'ENTRY':
            # Future CE and PE
            if instance.product == 'future':
                user_stock_config = AccountStockConfig.objects.get(
                                                        account=instance.account,
                                                        product=instance.product,
                                                        symbol=instance.symbol,
                                                        name=instance.name,
                                                        mode=instance.mode,
                                                        is_active=True)

                # Check Order is Place or Not
                if user_stock_config.order_placed or Is_Order_Completed(connection, user_stock_config.order_id):
                    user_stock_config.order_placed = True
                    user_stock_config.save()

                    # # Place Target Order
                    # if not user_stock_config.target_order_placed:
                    #     order_id, order_status = Create_Order(connection, 'SELL', 'CARRYFORWARD', instance.token, instance.symbol, instance.exchange, instance.fixed_target, instance.lot, "LIMIT")

                    #     if order_id in ['0', 0, None]:
                    #         print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Retry Because Order Placement failed")
                    #         AccountPlaceTargetStoplossOrder(sender, instance, created)

                    #     print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Successfully Placed Target Order")
                    #     user_stock_config.target_order_id = order_id
                    #     user_stock_config.target_order_placed = True
                    #     user_stock_config.save()
                    #     sleep(3)
                    # else:
                    #     print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} -  Target Order is Already Placed")
                    
                    
                    # # Place Stoploss Order
                    # if not user_stock_config.stoploss_order_placed:
                    #     order_id, order_status = Create_Order(connection, 'SELL', 'CARRYFORWARD', instance.token, instance.symbol, instance.exchange, instance.stoploss, instance.lot, "LIMIT")

                    #     if order_id in ['0', 0, None]:
                    #         print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Retry Because Order Placement failed")
                    #         AccountPlaceTargetStoplossOrder(sender, instance, created)

                    #     print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Successfully Placed Stoploss Order")
                    #     user_stock_config.stoploss_order_id = order_id
                    #     user_stock_config.stoploss_order_placed = True
                    #     user_stock_config.save()

                    # else:
                    #     print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} -  Stoploss Order is Already Placed")

                # Update the status if rejected or retry in 5 sec if status is open.pending
                else:
                    unique_order_id = user_stock_config.order_id.split('@')[0]
                    data = connection.individual_order_details(unique_order_id)
                    if data['data']['orderstatus'] in ['open', 'pending']:
                        print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Buy Order is not completed. Retry in 5 Sec")
                        sleep(5)
                        AccountPlaceTargetStoplossOrder(sender, instance, created)
                    else:
                        print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Order {data['data']['orderstatus']} - {data['data']['text']}")

                        # AccountTransaction.objects.filter(order_id=user_stock_config.order_id).delete()
                        # user_stock_config.delete()
                        # if ('RMS:Rule' in data['data']['text']) or ('F&O ban' in data['data']['text']) or ('Order price is beyond' in data['data']['text']):
                        #     StockConfig.objects.filter(symbol=instance.symbol, fixed_target=instance.fixed_target).delete()
                        #     Transaction.objects.filter(symbol=instance.symbol, fixed_target=instance.fixed_target).delete()
                        #     Symbol.objects.filter(name=instance.name).update(fno=False)

                        # Send Email Notification
                        subject = f"Fno Trade on {instance.symbol}" if instance.product == 'future' else f"Equity Trade on {instance.name}"
                        template = 'order_failed.html'
                        recipients = [instance.account.email]
                        email_context = {
                            'name': instance.account.first_name,
                            "symbol": instance.symbol,
                            "price": round(instance.price, 2),
                            "target": instance.fixed_target,
                            "stoploss": instance.stoploss,
                            "order_id": user_stock_config.order_id
                        }
                        email_send(subject, template, recipients, email_context)

            # Equity Delivery and INTRADAY(PE)
            elif instance.product == 'equity':
                sleep(10)
                user_stock_config = AccountStockConfig.objects.get(
                                                    account=instance.account,
                                                    product=instance.product,
                                                    symbol=instance.symbol,
                                                    name=instance.name,
                                                    mode=instance.mode,
                                                    is_active=True)

                # Equity Delivery
                if instance.mode == 'CE':
                    if user_stock_config.order_placed or Is_Order_Completed(connection, user_stock_config.order_id):
                        user_stock_config.order_placed = True
                        user_stock_config.save()
                    
                    # Update the status if rejected
                    else:
                        unique_order_id = user_stock_config.order_id.split('@')[0]
                        data = connection.individual_order_details(unique_order_id)
                        print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Order {data['data']['orderstatus']} - {data['data']['text']}")
                        user_stock_config.order_status = data['data']['text']
                        user_stock_config.save()
                
                # Equity INTRADAY(PE)
                else:
                    if user_stock_config.order_placed or Is_Order_Completed(connection, user_stock_config.order_id):
                        user_stock_config.order_placed = True
                        user_stock_config.save()

                        # # Place Target Order
                        # if not user_stock_config.target_order_placed:
                        #     order_id, order_status = Create_Order(connection, 'BUY', 'INTRADAY', instance.token, instance.symbol, instance.exchange, instance.fixed_target, instance.lot, "LIMIT")

                        #     if order_id in ['0', 0, None]:
                        #         print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Retry Because Order Placement failed")
                        #         AccountPlaceTargetStoplossOrder(sender, instance, created)

                        #     print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Successfully Placed Target Order")
                        #     user_stock_config.target_order_id = order_id
                        #     user_stock_config.target_order_placed = True
                        #     user_stock_config.save()
                        #     sleep(3)
                        # else:
                        #     print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} -  Target Order is Already Placed")

                        # # Place Stoploss Order
                        # if not user_stock_config.stoploss_order_placed:
                        #     order_id, order_status = Create_Order(connection, 'BUY', 'INTRADAY', instance.token, instance.symbol, instance.exchange, instance.stoploss, instance.lot, "LIMIT")

                        #     if order_id in ['0', 0, None]:
                        #         print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Retry Because Order Placement failed")
                        #         AccountPlaceTargetStoplossOrder(sender, instance, created)

                        #     print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Successfully Placed Stoploss Order")
                        #     user_stock_config.stoploss_order_id = order_id
                        #     user_stock_config.stoploss_order_placed = True
                        #     user_stock_config.save()

                        # else:
                        #     print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} -  Stoploss Order is Already Placed")

                    # Update the status if rejected or retry in 5 sec if status is open.pending
                    else:
                        unique_order_id = user_stock_config.order_id.split('@')[0]
                        data = connection.individual_order_details(unique_order_id)
                        if data['data']['orderstatus'] in ['open', 'pending']:
                            print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Buy Order is not completed. Retry in 5 Sec")
                            sleep(5)
                            AccountPlaceTargetStoplossOrder(sender, instance, created)
                        else:
                            print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Order {data['data']['orderstatus']} - {data['data']['text']}")

                            # AccountTransaction.objects.filter(order_id=user_stock_config.order_id).delete()
                            # user_stock_config.delete()
                            # if ('RMS:Rule' in data['data']['text']) or ('F&O ban' in data['data']['text']) or ('Order price is beyond' in data['data']['text']):
                            #     StockConfig.objects.filter(symbol=instance.symbol, fixed_target=instance.fixed_target).delete()
                            #     Transaction.objects.filter(symbol=instance.symbol, fixed_target=instance.fixed_target).delete()

                            # Send Email Notification
                            subject = f"Fno Trade on {instance.symbol}" if instance.product == 'future' else f"Equity Trade on {instance.name}"
                            template = 'order_failed.html'
                            recipients = [instance.account.email]
                            email_context = {
                                'name': instance.account.first_name,
                                "symbol": instance.symbol,
                                "price": round(instance.price, 2),
                                "target": instance.fixed_target,
                                "stoploss": instance.stoploss,
                                "order_id": user_stock_config.order_id
                            }
                            email_send(subject, template, recipients, email_context)

            else:
                print(f"MoneyBall: Account Place Target Stoploss Order: {instance.account.first_name} {instance.account.last_name} - {instance.account.user_id} - Invalid product {instance.product}")
        else:
            print(f"MoneyBall: Account Place Target Stoploss Order: Not allowed on account transaction indicator : {instance.indicate}")
    except Exception as e:
        print(f"MoneyBall: Account Place Target Stoploss Order: Error Trade Func: {e}")
    return True


@receiver(post_save, sender=Transaction)
def OnAlgoTransaction(sender, instance, created, **kwargs):
  if created:
    sleep(1)
    transaction.on_commit(lambda: AccountTradeAction(sender, instance, created))


@receiver(post_save, sender=AccountTransaction)
def OnAccountTransaction(sender, instance, created, **kwargs):
  if created:
    sleep(1)
    transaction.on_commit(lambda: AccountPlaceTargetStoplossOrder(sender, instance, created))
