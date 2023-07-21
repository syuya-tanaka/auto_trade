"""Prepare everything you need for the app."""
import os
import logging
from typing import Final
from typing import TypeVar

from envyaml import EnvYAML
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session as S
from sqlalchemy.orm import sessionmaker


env = EnvYAML('/src/app/config.yml')

dialect = env['db.dialect']
driver = env['db.driver']
user = env['db.user']
password = env['db.password']
host = env['db.host']
port = env['db.port']
db_name = env['db.name']
db_url = f'{dialect}+{driver}://{user}:{password}@{host}:{port}/{db_name}'

engine = create_engine(db_url, echo=True)
Base = declarative_base()
Session = sessionmaker(engine)

_S = TypeVar('_S', sessionmaker, S, covariant=True)

ACCOUNT_ID: Final = env['oanda.account_id']
DEMO_ACCOUNT_ID: Final = env['oanda.demo_account_id']
ACCESS_TOKEN: Final = env['oanda.access_token']

# granularity
M5: Final = 'M5'
M15: Final = 'M15'
M30: Final = 'M30'
H1: Final = 'H1'
H4: Final = 'H4'
D1: Final = 'D1'

log_file = os.path.dirname(__file__) + '/method_log.log'

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(threadName)s ' +
                      'func:%(funcName)s %(message)s'
        },
    },
    'handlers': {
        'defaultHandlers': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': logging.DEBUG
        },
        'modelsHandlers': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': logging.DEBUG
        },
        'devHandlers': {
            'class': 'logging.FileHandler',
            'filename': log_file,
            'formatter': 'standard',
            'level': logging.DEBUG
        },
        'prodHandlers': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': logging.INFO
        },
    },
    'root': {
        'handlers': ['defaultHandlers'],
        'level': logging.WARNING,
    },
    'loggers': {
        'models_base': {
            'handlers': ['modelsHandlers'],
            'level': logging.DEBUG,
            'propagate': 0
        },
        'models_candle': {
            'handlers': ['modelsHandlers'],
            'level': logging.DEBUG,
            'propagate': 0
        },
        'dev': {
            'handlers': ['devHandlers'],
            'level': logging.DEBUG,
            'propagate': 0
        },
        'oanda': {
            'handlers': ['modelsHandlers'],
            'level': logging.DEBUG,
            'propagate': 0
        },
    },
}
