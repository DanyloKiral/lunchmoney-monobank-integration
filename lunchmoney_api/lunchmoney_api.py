import requests

from utils import now, add_days


class LunchmoneyApi:
    def __init__(self, configs, credentials):
        self.baseUrl = configs.get('baseUrl')
        self.routes = configs.get('routes')
        self.headers = {
            'Authorization': f'Bearer {credentials.get("token")}',
            'Content-Type': 'application/json'
        }
        self.options = configs.get('options')

    def get_accounts(self):
        url = self.__format_uri(self.routes.get('accounts'))
        response = requests.get(url, headers=self.headers)
        assert response.ok, f'Lunchmoney API get_accounts error: {response.json()}'

        return response.json().get('assets')

    def get_latest_transactions(self, account_id):
        start_date = add_days(now(), -1 * int(self.options.get('check_transaction_for_last_n_days')))
        url = self.__format_uri(self.routes.get('transactions'))
        response = requests.get(url, headers=self.headers, params={
            "start_date": str(start_date.date()),
            "end_date": str(now().date()),
            "asset_id": account_id
        })
        assert response.ok, f'Lunchmoney API get_latest_transactions error: {response.json()}'

        return response.json().get('transactions')

    def __format_uri(self, route):
        return f'{self.baseUrl}/{route}'


