"""socket client."""
import _pickle
import pickle
import socket


def run(args):
    server_ip, port = '172.18.0.2', 9901
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, port))
        s.send(bytes(args, 'utf-8'))
        print(f'send_message: {args}')
        while True:
            recv_data = s.recv(37888)
            try:
                obj = pickle.loads(recv_data)
                print(f'received data: {obj}', len(obj))
            except _pickle.UnpicklingError:
                pass
            except ValueError:
                pass
            except EOFError:
                print('done!')
                break
