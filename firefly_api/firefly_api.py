import json
import logging
import requests
from utils import now, add_days

class FireflyApi:
    def __init__(self, configs, credentials):
        self.baseUrl = configs.get("baseUrl")
        self.routes = configs.get("routes")
        self.headers = {
            "Authorization": f"Bearer {credentials.get('token')}",
            "Content-Type": "application/json",
            "accept": "application/vnd.api+json",
        }
        self.options = configs.get("options")

    def get_accounts(self):
        url = self.__format_uri(self.routes.get("accounts"))
        response = requests.get(url, headers=self.headers, params={
            "type": "asset"
        })
        assert response.ok, f"FireflyApi API get_accounts error: {response.json()}"

        return [{
            "id": acc["id"],
            "name": acc["attributes"]["name"],
            "currency": acc["attributes"]["currency_code"].upper()
        } for acc in response.json().get("data")]
    
    def get_latest_transactions(self, account_id):
        start_date = add_days(now(), -1 * int(self.options.get("check_transaction_for_last_n_days")))
        url = self.__format_uri(self.routes.get("accounts") + f"/{account_id}/transactions")
        response = requests.get(url, headers=self.headers, params={
            "start": str(start_date.date()),
            "end": str(now().date())
        })
        assert response.ok, f"FireflyApi get_latest_transactions error: {response.json()}"

        return [{
            "external_id": trans["external_id"],
            "date": trans["date"] 
        } for trans_group in response.json().get("data") for trans in trans_group["attributes"]["transactions"]]
    
    def insert_transactions(self, transaction_list: list):
        url = self.__format_uri(self.routes.get("transactions"))
        for transaction in transaction_list: 
            try:
                data = {
                    "error_if_duplicate_hash": False,
                    "apply_rules": True,
                    "fire_webhooks": True,
                    "group_title": "",
                    "transactions": [transaction]
                }
                response = requests.post(url, headers=self.headers, data=json.dumps(data))
                data = response.json()
                assert response.ok, f"FireflyApi API insert_transactions error: {response.json()}"
                assert response.status_code != 204, 'FireflyApi API insert_transactions returns empty response'
            except Exception as ex:
                logging.warning(f"Error during transaction insert. Exception = {ex}")
                
    
    def __format_uri(self, route):
        return f"{self.baseUrl}/{route}"