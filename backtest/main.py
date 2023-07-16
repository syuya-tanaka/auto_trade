import datetime

# from app.models.candlesticks import UsdJpyBaseCandle5m
from app.oanda.oanda import AccountAPI
from app.oanda.oanda import RequestAPI
from app.settings import ACCESS_TOKEN
from app.settings import ACCOUNT_ID


print('this is main.py')

if __name__ == '__main__':
    response = AccountAPI.access_account()
    print(response)
    api_client = RequestAPI()
    r = api_client.request_data()
    print(r)
