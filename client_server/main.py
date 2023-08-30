"""Get candlestick data."""
import argparse

from controllers import socket_client


def main():
    parser = argparse.ArgumentParser(description='Get candlestick data.')
    parser.add_argument('--granularity', help='specify which granularity to use.')
    dict_args = vars(parser.parse_args())
    socket_client.run(dict_args['granularity'])


if __name__ == '__main__':
    main()
