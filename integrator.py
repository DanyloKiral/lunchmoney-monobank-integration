import datetime

from utils import load_credentials, load_configs, save_to_json_file
import logging
from mono_api import MonoApi


def configure_logging():
    # todo: add file and console handlers

    logging.basicConfig(
        filename='logs/logs.log',
        format='%(asctime)s %(name)s:%(levelname)s - %(message)s',
        level=logging.DEBUG
    )


def main():
    configure_logging()

    logging.debug('app started')

    configs = load_configs()
    credentials = load_credentials()

    mono_api = MonoApi(configs.get('mono'), credentials.get('mono'))

    client_info = mono_api.get_client_info()
    save_to_json_file(client_info, 'data/client_info.json')

    from_date = datetime.datetime.now() + datetime.timedelta(days=-31)
    statement = mono_api.get_statement('0', from_date)
    save_to_json_file(statement, 'data/statement.json')

    logging.debug('fin')


if __name__ == '__main__':
    main()
