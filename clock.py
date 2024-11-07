import tzlocal
from apscheduler.schedulers.background import BackgroundScheduler
from task import BrokerConnection, CheckLtp, socket_setup, stay_awake, stop_socket_setup


def start():
    sched = BackgroundScheduler(timezone=str(tzlocal.get_localzone()), daemon=True)

    socket_setup(log_identifier='Restart')

    # Schedules job_function to be run on the Monday to Friday
    sched.add_job(stay_awake, 'cron',
                minute='*/2', timezone='Asia/Kolkata')
    sched.add_job(BrokerConnection, 'cron',
                hour='9', minute='11', timezone='Asia/Kolkata')
    sched.add_job(socket_setup, 'cron',
                hour='9', minute='12', timezone='Asia/Kolkata')
    sched.add_job(CheckLtp, 'cron', day_of_week='mon-fri', max_instances=2,
                hour='9-15', second='*/30', timezone='Asia/Kolkata')
    # sched.add_job(stop_socket_setup, 'cron', day_of_week='mon-fri',
    #             hour='5', minute='5', timezone='Asia/Kolkata')
    sched.start()
    return True
