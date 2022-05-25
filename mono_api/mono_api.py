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

        return response.json()

    def get_client_info(self):
        url = self.__format_uri(self.routes.get('client_info'))
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_client_info(self):
        url = self.__format_uri(self.routes.get('client_info'))
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_statement(self):
        url = self.__format_uri(self.routes.get('statement'))
        response = requests.get(url, headers=self.headers)
        return response.json()

    def init_webhook(self, webhook_url):
        url = self.__format_uri(self.routes.get('webhook_init'))
        data = {
            'webHookUrl': webhook_url
        }
        response = requests.post(url, headers=self.headers, data=data)
        return response.json()

    def __format_uri(self, route):
        return f'{self.baseUrl}/{route}'
