import datetime

from app import settings
from app.models import base
from app.models import candlesticks
from app.models.candlesticks import UsdJpyBaseCandle5m


print('this is main.py')

date = datetime.datetime.now()
UsdJpyBaseCandle5m.create(date, 1.0, 2.0, 3.0, 4.0, 4)
