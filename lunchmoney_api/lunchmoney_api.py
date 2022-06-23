import json
import logging

import requests

from utils import now, add_days


class LunchmoneyApi:
    def __init__(self, configs, credentials):
        self.baseUrl = configs.get("baseUrl")
        self.routes = configs.get("routes")
        self.headers = {
            "Authorization": f"Bearer {credentials.get('token')}",
            "Content-Type": "application/json"
        }
        self.options = configs.get("options")

    def get_accounts(self):
        url = self.__format_uri(self.routes.get("accounts"))
        response = requests.get(url, headers=self.headers)
        assert response.ok, f"Lunchmoney API get_accounts error: {response.json()}"

        return response.json().get("assets")

    def get_latest_transactions(self, account_id):
        start_date = add_days(now(), -1 * int(self.options.get("check_transaction_for_last_n_days")))
        url = self.__format_uri(self.routes.get("transactions"))
        response = requests.get(url, headers=self.headers, params={
            "start_date": str(start_date.date()),
            "end_date": str(now().date()),
            "asset_id": account_id
        })
        assert response.ok, f"Lunchmoney API get_latest_transactions error: {response.json()}"

        return response.json().get("transactions")

    def insert_transactions(self, transaction_list: list):
        url = self.__format_uri(self.routes.get("transactions"))
        data = {
            "transactions": transaction_list,
            "apply_rules": True,
            "skip_duplicates": False,
            "check_for_recurring": True,
            "debit_as_negative": True,
            "skip_balance_update": False
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        assert response.ok, f"Lunchmoney API insert_transactions error: {response.json()}"
        assert response.status_code != 204, 'Lunchmoney API insert_transactions returns empty response'

        ids = response.json()["ids"]
        assert len(ids) == len(transaction_list), f"Quantity of IDs of newly created transactions should correspond " \
                                                  f"to quantity of transactions to add. " \
                                                  f"Len IDs = {len(ids)}, Len of Transactions = {len(transaction_list)}"
        for index, transaction in enumerate(transaction_list):
            tr_id = ids[index]
            transaction["id"] = tr_id

        return transaction_list

    def create_transaction_group(self, group):
        url = self.__format_uri(self.routes.get("transaction_group"))
        response = requests.post(url, headers=self.headers, data=json.dumps(group))
        assert response.ok, f"Lunchmoney API create_transaction_group error: {response.json()}"
        group_id = response.json()
        logging.info(f'Lunchmoney API create_transaction_group response: {group_id}')

    def get_transaction_group(self, group_id):
        url = self.__format_uri(self.routes.get("transaction_group")) + str(group_id)
        response = requests.get(url, headers=self.headers)
        group = response.json()
        return group

    def __format_uri(self, route):
        return f"{self.baseUrl}/{route}"


