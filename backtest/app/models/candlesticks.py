"""table definition."""
import logging.config
from threading import RLock
from typing import List
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Float

from app.models.base import session_scope
from app.settings import Base
from app.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('models_candle')


class BaseMixin(object):
    time = Column(DateTime, primary_key=True, nullable=False)
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Integer)

    @classmethod
    def fetch_data_in_desc_order(cls, rlock: RLock):
        """Fetch data in descending order."""
        with session_scope(rlock) as session:
            query_obj = session.query(cls).order_by(cls.time.asc())
    
        return query_obj


class UsdJpyBaseCandle5m(BaseMixin, Base):
    __tablename__ = 'usd_jpy_5m'


class UsdJpyBaseCandle15m(BaseMixin, Base):
    __tablename__ = 'usd_jpy_15m'


class UsdJpyBaseCandle30m(BaseMixin, Base):
    __tablename__ = 'usd_jpy_30m'


class UsdJpyBaseCandle1h(BaseMixin, Base):
    __tablename__ = 'usd_jpy_1h'


class UsdJpyBaseCandle4h(BaseMixin, Base):
    __tablename__ = 'usd_jpy_4h'


class UsdJpyBaseCandle1d(BaseMixin, Base):
    __tablename__ = 'usd_jpy_1d'


# granularity: the_class_itself in dict
candle_class = {
    'M5': UsdJpyBaseCandle5m,
    'M15': UsdJpyBaseCandle15m,
    'M30': UsdJpyBaseCandle30m,
    'H1': UsdJpyBaseCandle1h,
    'H4': UsdJpyBaseCandle4h,
    'D': UsdJpyBaseCandle1d,
                }
