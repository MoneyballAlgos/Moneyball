import json
import threading
from zoneinfo import ZoneInfo
from datetime import datetime
from django.http import HttpResponse
from account.action import AccountExitAction
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def AwakeAPI(request):
    try:
        return HttpResponse(True)
    except Exception as e:
        return HttpResponse(str(e))


# Create your views here.
@csrf_exempt
def AccountExitApi(request):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        print(f"MoneyBall: Account Exit Api : Started {now.strftime('%d-%b-%Y %H:%M:%S')}")
        data = json.loads(request.body)

        # Streaming threads for Open Positions
        exit_thread = threading.Thread(name=f"API-Exit-{now.strftime('%d-%b-%Y %H:%M:%S')}", target=AccountExitAction, args=(data), daemon=True)
        exit_thread.start()

        print(f'MoneyBall: Account Exit Api : Execution Time(hh:mm:ss) : {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
        return HttpResponse(True)
    except Exception as e:
        return HttpResponse(str(e))