"""oanda api used for backtesting."""
from datetime import datetime
from datetime import timedelta
import logging.config
import json
from queue import Queue
from typing import Callable
from typing import Final

import requests

from app.oanda.utils import endpoint
from app.oanda.utils import generate_date
from app.oanda.utils import stopper_for_each_time
from app.models.candlesticks import candle_class
from app.settings import ACCOUNT_ID
from app.settings import ACCESS_TOKEN
from app.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('dev')

OANDA_URL: Final = 'https://api-fxtrade.oanda.com/'
HEADERS: Final = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
START: Final = None
END: Final = None
INSTRUMENT: Final = 'USD_JPY'
REQUESTS_COUNT: Final = 5000
CANDLE_FORMAT: Final = 'midpoint'
GRANULARITY: Final = 'M5'
DAILY_ALIGNMENT: Final = 6
ALIGNMENT_TIMEZONE: Final = 'Asia/Tokyo'


@endpoint('v3/accounts')
class AccountAPI(object):

    ENDPOINT = ""

    def __init__(self,
                 account_id: str = ACCOUNT_ID,
                 access_token: str = ACCESS_TOKEN) -> None:
        self.account_id = account_id
        self.access_token = access_token

    def __str__(self) -> str:
        return f'account_id={self.account_id},' \
                f'access_token={self.access_token}'

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


@endpoint(f'v3/instruments/{INSTRUMENT}/candles?')
class RequestAPI(AccountAPI):

    def __init__(self,
                 account_id: str = ACCOUNT_ID,
                 access_token: str = ACCESS_TOKEN) -> None:
        super().__init__(account_id, access_token)

    def get_to_time(self,
                    count: int,
                    days: int,
                    time: int) -> str:
        """Get 'to_time'.
        Args:
            count (int): This is for checking the number of laps.
            days (int): count_each_granularity(granularity)'s reutrn.
                        The number of days that decreases each cycle.
            time (int): Each granularity
        """
        if count * days > stopper_for_each_time(time):
            print(f'{time} is Finish.')
            exit()

        days_ago = count * days
        date = generate_date(days_offset=days_ago)
        return date.isoformat(timespec='seconds')

    def get_from_time(self, count: int, days: int, time: int) -> str:
        if count == 1:
            days_differencial = datetime.now() - timedelta(3652)
            return days_differencial.isoformat(timespec='seconds')
        else:
            return self.get_to_time(count - 1, days, time)

    def create_url(self,
                   granularity: str,
                   start: str,
                   end: str,
                   candle_format: str = CANDLE_FORMAT,
                   alignment_timezone: str = ALIGNMENT_TIMEZONE,
                   daily_alignment: int = DAILY_ALIGNMENT,
                   ) -> str:
        return self.ENDPOINT + f'from={start}&'\
                               f'to={end}&'\
                               f'candleFormat={candle_format}&'\
                               f'granularity={granularity}&'\
                               f'dailyAlignment={daily_alignment}&'\
                               f'alignmentTimezone={alignment_timezone}'

    def request_data(self,
                     granularity: str,
                     start: Callable,
                     end: Callable,
                     count: int,
                     days: int,
                     time: int,
                     queue: "Queue"):
        request_url = OANDA_URL + self.create_url(
                                        granularity=granularity,
                                        start=start(count, days, time),
                                        end=end(count, days, time)
                                        )
        r = requests.get(request_url, headers=HEADERS)
        if r.status_code == 200:
            logger.debug({
                'action': 'request candles',
                'status': 'request success.',
                'request_url': r.url,
                })
            queue.put(json.loads(r.content))
            return

        logger.debug({
            'action': 'request candles',
            'status': 'request fail.',
            'request_url': r.url,
            'message': r.content,
        })
        return request_url, r.content, r

