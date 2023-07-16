"""oanda api used for backtesting."""
from datetime import datetime
import logging.config
from typing import Final
from typing import Optional

import requests

from app.oanda.utils import count_each_granularity
from app.oanda.utils import endpoint
from app.oanda.utils import generate_date
from app.oanda.utils import hand_the_class
from app.oanda.utils import stopper_for_each_time
from app.models.candlesticks import candle_class
from app.settings import ACCOUNT_ID
from app.settings import ACCESS_TOKEN
from app.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('oanda')

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


@endpoint(f'v3/instruments/{INSTRUMENT}/candles?')
class RequestAPI(AccountAPI):

    def __init__(self,
                 account_id: str = ACCOUNT_ID,
                 access_token: str = ACCESS_TOKEN) -> None:
        super().__init__(account_id, access_token)

    def get_from_time(self,
                      count: int,
                      days: int,
                      time: int) -> datetime:
        """Get 'from_time'.
        Args:
            count (int): This is for checking the number of laps.
            days (int): count_each_granularity(granularity)'s reutrn.
                        The number of days that decreases each cycle.
        """
        if count * days > stopper_for_each_time(time):
            print(f'{time} is Finish.')

        if count == 1:
            date = generate_date(days_offset=count)
            return date

        days_ago = count * days
        date = generate_date(days_offset=days_ago)
        return date

    def create_url(self,
                   granularity: str,
                   start: datetime,
                   end: Optional[datetime] = None,
                   count: int = 5000,
                   candle_format: str = CANDLE_FORMAT,
                   instrument: str = 'USD_JPY',
                   alignment_timezone: str = ALIGNMENT_TIMEZONE,
                   daily_alignment: int = DAILY_ALIGNMENT,
                   ) -> str:
                            # f'to={end}&'\     ←一時的に外している。
        self.ENDPOINT += f'count={count}&'\
                            f'from={start}&'\
                            f'candleFormat={candle_format}&'\
                            f'granularity={granularity}&'\
                            f'dailyAlignment={daily_alignment}&'\
                            f'alignmentTimezone={alignment_timezone}'
        return self.ENDPOINT

    def request_data(self):
        request_url = OANDA_URL + self.create_url(granularity='H1',
                                                  start=generate_date().isoformat())
        r = requests.get(request_url, headers=HEADERS)
        if r.status_code == 200:
            logger.debug({
                'action': 'request candles',
                'status': 'request success.',
                'request_url': request_url,
                })
            return r.content
        logger.debug({
            'action': 'request candles',
            'status': 'request fail.',
            'request_url': request_url,
            'message': r.content,
        })
        return request_url, r.content, r
