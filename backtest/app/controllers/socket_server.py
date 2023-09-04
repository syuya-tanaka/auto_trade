"""socket server."""
import logging
import logging.config
import pickle
import socketserver
from threading import RLock

from app.oanda.utils import from_granularity_to_model
from app.models.candlesticks import candle_class
from app.models.base import count_candles_data
from app.models.base import fetch_desc_data_from_data
from app.settings import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('dev')

server_address = ('172.18.0.2', 9901)


class OriginalRequestHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        super().handle()
        recv_data = self.request.recv(1024).decode('utf-8')
        print('received message', recv_data)

        if count_candles_data(candle_class[recv_data]):
            rlock = RLock()
            # fetch_desc_data_from_data()の第一引数は外部サーバーから送られてきたデータを入れる。
            desc_data, data_count = fetch_desc_data_from_data(
                                                recv_data,
                                                from_granularity_to_model,
                                                rlock)
            gen_desc_data = (data for data in desc_data)
            loop_count = 1
            count = 0
            pickle_list = []
            for data in gen_desc_data:
                count += 1

                candle_data = {
                    'time': data.time,
                    'open': data.open,
                    'close': data.close,
                    'high': data.high,
                    'low': data.low,
                    'volume': data.volume
                }

                if count >= 500 or (data_count / loop_count) - 1 == loop_count:
                    pickled = pickle.dumps(pickle_list)
                    print(pickle_list, len(pickled))
                    self.request.send(pickled)
                    pickle_list.clear()
                    count = 0
                    loop_count += 1
                
                else:
                    pickle_list.append(candle_data)

        logger.debug({
            'action': 'handle the request',
            'status': 'success',
            'client address': self.client_address,
            'received data': recv_data
        })


def socket_server_run():
    with socketserver.TCPServer(server_address,
                                OriginalRequestHandler) as httpd:
        print('Accepting')
        httpd.serve_forever()
