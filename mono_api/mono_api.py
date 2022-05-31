from datetime import datetime
from utils import datetime_to_unix, now
import requests


class MonoApi:
    def __init__(self, configs, credentials):
        self.baseUrl = configs.get('baseUrl')
        self.routes = configs.get('routes')
        self.headers = {
            'X-Token': credentials.get('token'),
            'Content-Type': 'application/json'
        }

    def get_exchange_rates(self):
        url = self.__format_uri(self.routes.get('exchange_rates'))
        response = requests.get(url)
        assert response.ok, f'Mono API get_exchange_rates error: {response.json()}'

        return response.json()

    def get_client_info(self):
        url = self.__format_uri(self.routes.get('client_info'))
        response = requests.get(url, headers=self.headers)
        assert response.ok, f'Mono API get_client_info error: {response.json()}'

        return response.json()

    def get_statement(self, account_id, from_date: datetime, to_date: datetime = None):
        from_unix = datetime_to_unix(from_date)
        to_unix = datetime_to_unix(datetime.now() if to_date is None else to_date)

        route_with_params = self.routes.get('statement')\
            .replace('{account}', account_id)\
            .replace('{from}', str(from_unix))\
            .replace('{to}', str(to_unix))

        url = self.__format_uri(route_with_params)
        response = requests.get(url, headers=self.headers)
        assert response.ok, f'Mono API get_statement error: {response.json()}'

        return response.json()

    def init_webhook(self, webhook_url):
        url = self.__format_uri(self.routes.get('webhook_init'))
        data = {
            'webHookUrl': webhook_url
        }
        response = requests.post(url, headers=self.headers, data=data)
        assert response.ok, f'Mono API init_webhook error: {response.json()}'
        return response.json()

    def __format_uri(self, route):
        return f'{self.baseUrl}/{route}'
