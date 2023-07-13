import datetime

# from app.models.candlesticks import UsdJpyBaseCandle5m
from app.oanda.oanda import AccountAPI
from app.settings import ACCESS_TOKEN
from app.settings import ACCOUNT_ID


print('this is main.py')

if __name__ == '__main__':
    respose = AccountAPI.access_account()
    print(respose)
