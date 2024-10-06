import tzlocal
from django.contrib.auth.models import User
from apscheduler.schedulers.background import BackgroundScheduler
from task import AccountConnection, BrokerConnection, MarketDataUpdate, SquareOff, stay_awake, SymbolSetup, Equity_BreakOut_1, FnO_BreakOut_1


def start():
    sched = BackgroundScheduler(timezone=str(tzlocal.get_localzone()), daemon=True)
    if not User.objects.filter(username='Master').exists():
        User.objects.create_superuser(
            username='Master',
            password='admin'
        )
        print('Superuser has been created.')
    if not User.objects.filter(username='MoneyBall').exists():
        User.objects.create_user(
            username='MoneyBall',
            password='admin'
        )
        print('Staff User has been created.')
    if not User.objects.filter(username='User').exists():
        User.objects.create_user(
            username='User',
            password='user'
        )
        print('User has been created.')

    # Schedules job_function to be run on the Monday to Friday
    sched.add_job(stay_awake, 'cron', day_of_week='mon-fri',
                second='*/40', timezone='Asia/Kolkata')
    sched.add_job(BrokerConnection, 'cron', day_of_week='mon-fri',
                hour='9', minute='0', timezone='Asia/Kolkata')
    sched.add_job(SymbolSetup, 'cron', day_of_week='mon-fri',
                hour='9', minute='2', timezone='Asia/Kolkata')
    sched.add_job(AccountConnection, 'cron', day_of_week='mon-fri',
                hour='9', minute='10', timezone='Asia/Kolkata')
    sched.add_job(MarketDataUpdate, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/10', timezone='Asia/Kolkata')
    sched.add_job(SquareOff, 'cron', day_of_week='mon-fri',
                hour='15', minute='17', timezone='Asia/Kolkata')
    sched.add_job(Equity_BreakOut_1, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/5', timezone='Asia/Kolkata')
    sched.add_job(FnO_BreakOut_1, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/5', timezone='Asia/Kolkata')
    sched.start()
    return True
