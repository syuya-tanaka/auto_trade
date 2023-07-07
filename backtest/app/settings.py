"""Prepare everything you need for the app."""
import logging

from envyaml import EnvYAML
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
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
session = sessionmaker(engine)

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
        }
    }
}
