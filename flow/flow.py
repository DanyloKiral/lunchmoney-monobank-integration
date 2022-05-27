import logging
import time

from datetime import datetime
from flow.mapper import Mapper
from utils import add_days, save_to_json_file
from mono_api import MonoApi
from lunchmoney_api import LunchmoneyApi


class ImportFlow:
    def __init__(self, configs, credentials):
        self.configs = configs
        self.api_credentials = credentials

        self.mono_api = MonoApi(configs.get('mono'), credentials.get('mono'))
        self.lunchmoney_api = LunchmoneyApi(configs.get('lunchmoney'), credentials.get('lunchmoney'))
        logging.info('initiated apis')

    def run_import(self):
        accounts_mapping = self.create_account_mappings()
        logging.info('created account mappings')

        new_transactions = []
        for account in accounts_mapping:
            lunch_acc = account.get('lunch_acc')
            mono_acc = account.get('mono_acc')
            logging.info(f'loading transactions for account {lunch_acc.get("name")}')

            latest_transactions = self.lunchmoney_api.get_latest_transactions(lunch_acc.get('id'))
            transactions_per_date = self.__group_transaction_per_date(latest_transactions)

            import_from_date, same_day_ids = self.__get_import_params(transactions_per_date, lunch_acc)
            new_account_transactions = self.mono_api.get_statement(
                mono_acc.get('id'),
                from_date=import_from_date
            )
            account['new_account_transactions'] = new_account_transactions
            new_transactions = new_transactions + Mapper.map_to_lunch_transactions(new_account_transactions, lunch_acc)
            if len(new_account_transactions) > 0:
                logging.info(f'loaded {len(new_account_transactions)} new transactions for account {lunch_acc.get("name")}')
            else:
                logging.info(f'no new transactions for account {lunch_acc.get("name")} found')
            time.sleep(60)
        logging.info('checked all accounts for new transactions')

        save_to_json_file(accounts_mapping, 'data/accounts_mapping.json')

    def create_account_mappings(self):
        mono_accounts = self.mono_api.get_client_info().get('accounts')
        lunch_accounts = self.lunchmoney_api.get_accounts()
        accounts_mapping = Mapper.create_accounts_mapping(
            self.configs.get('mappings').get('accounts'),
            mono_accounts,
            lunch_accounts
        )
        return accounts_mapping

    @staticmethod
    def __group_transaction_per_date(latest_transactions: list):
        transactions_per_date = {}
        for trans in latest_transactions:
            date_trans_list = transactions_per_date.setdefault(trans.get('date'), [])
            transaction_external_id = trans.get('external_id')
            if transaction_external_id is not None:
                date_trans_list.append(transaction_external_id)
        return transactions_per_date

    @staticmethod
    def __get_import_params(transactions_per_date: dict, lunch_acc):
        if len(transactions_per_date.keys()) == 0:
            created_at_date = lunch_acc.get('created_at').split('T')[0]
            return datetime.strptime(created_at_date, "%Y-%m-%d").date(), []
        last_transaction_date = max(transactions_per_date.keys())
        same_day_ids = transactions_per_date.get(last_transaction_date)
        start_date = datetime.strptime(last_transaction_date, "%Y-%m-%d").date()
        if len(same_day_ids) == 0:
            start_date = add_days(start_date, 1)
        return start_date, same_day_ids
