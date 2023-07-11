"""table definition."""
import logging.config

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Float

from app.models.base import Base
from app.models.base import session_scope
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
    def create(cls, time, open, close, high, low, volume) -> None:
        candle = cls(time=time,
                     open=open,
                     close=close,
                     high=high,
                     low=low,
                     volume=volume)
        with session_scope() as session:
            session.add(candle)
        logger.debug({
            'action': 'create a ORM-object.',
            'status': 'success'
        })


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
