"""oanda api used for backtesting."""
# import aiohttp
import asyncio
import logging.config
from typing import Type

import requests

from app.oanda.utils import endpoint
from app.settings import ACCOUNT_ID
from app.settings import ACCESS_TOKEN
from app.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('oanda')

OANDA_URL = 'https://api-fxtrade.oanda.com/'
HEADERS = {'Authorization': f'Bearer {ACCESS_TOKEN}'}


@endpoint('v3/account')
class AccountAPI(object):

    ENDPOINT = ""

    def __init__(self, account_id: str, access_token: str) -> None:
        self.account_id = account_id
        self.access_token = access_token

    def __repr__(self) -> str:
        return f'account_id={self.account_id}, \
                access_token={self.access_token}'

    @classmethod
    def access_account(cls) -> str | ValueError:
        request_url = OANDA_URL + cls.ENDPOINT
        r = requests.get(request_url, headers=HEADERS)
        if r.status_code == 200:
            return f'status: {r.status_code} text: {r.text}'
        try:
            raise ValueError(f'{request_url} \n{r.text}')
        except ValueError as error:
            return error
