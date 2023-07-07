"""table definition."""
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer

from app.settings import Base


class BaseMixin(object):
    time = Column(DateTime, primary_key=True, nullable=False)
    open = Column(Integer)
    close = Column(Integer)
    high = Column(Integer)
    low = Column(Integer)
    volume = Column(Integer)


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
