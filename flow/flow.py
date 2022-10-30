import logging
import time

from datetime import datetime
from flow.mapper import Mapper
from utils import add_days, save_to_json_file, now
from mono_api import MonoApi
from lunchmoney_api import LunchmoneyApi


class ImportFlow:
    def __init__(self, configs, credentials):
        self.configs = configs
        self.api_credentials = credentials

        self.mono_api = MonoApi(configs["mono"], credentials["mono"])
        self.lunchmoney_api = LunchmoneyApi(configs["lunchmoney"], credentials["lunchmoney"])
        logging.info("initiated apis")

    def run_import(self):
        requests_interval_sec = self.configs["mono"]["options"]["requests_interval_sec"]
        accounts_mapping = self.create_account_mappings()
        logging.info("created account mappings")

        new_transactions = []
        number_of_iterations_left = len(accounts_mapping)
        for account in accounts_mapping:
            number_of_iterations_left -= 1
            lunch_acc = account["lunch_acc"]
            mono_acc = account["mono_acc"]
            logging.info(f"loading transactions for account {lunch_acc['name']}")

            latest_transactions = self.lunchmoney_api.get_latest_transactions(lunch_acc["id"])
            transactions_per_date = self.__group_transaction_per_date(latest_transactions)

            import_from_date, same_day_ids = self.__get_import_params(transactions_per_date)
            new_account_transactions = self.mono_api.get_statement(
                mono_acc["id"],
                from_date=import_from_date
            )
            new_account_transactions = self.__filter_transactions(latest_transactions, new_account_transactions)

            account["new_account_transactions"] = new_account_transactions
            new_transactions = new_transactions + Mapper.map_to_lunch_transactions(
                new_account_transactions, lunch_acc, self.configs["mono"]["options"]["add_mcc_tag"])
            if len(new_account_transactions) > 0:
                logging.info(f"loaded {len(new_account_transactions)} new transactions for account {lunch_acc['name']}")
            else:
                logging.info(f"no new transactions for account {lunch_acc['name']} found")
            if number_of_iterations_left > 0:
                time.sleep(requests_interval_sec)
        logging.info("checked all accounts for new transactions")
        # save_to_json_file(accounts_mapping, "data/accounts_mapping.json")
        transaction_monoid_to_lunchid = self.save_transactions(new_transactions)
        logging.info("inserted transactions to Lunchmoney")
        mono_tr_groups = self.save_transfer_groups(accounts_mapping, transaction_monoid_to_lunchid)
        # save_to_json_file(mono_tr_groups, "data/mono_tr_groups.json")
        logging.info("inserted transactions groups to Lunchmoney")

    def create_account_mappings(self):
        client_info = self.mono_api.get_client_info()
        lunch_accounts = self.lunchmoney_api.get_accounts()
        accounts_mapping = Mapper.create_accounts_mapping(
            self.configs["mappings"]["accounts"],
            client_info,
            lunch_accounts
        )
        return accounts_mapping

    def save_transactions(self, transactions):
        transactions = self.lunchmoney_api.insert_transactions(transactions)
        transaction_monoid_to_lunchid = {tr["external_id"]: tr["id"] for tr in transactions}
        return transaction_monoid_to_lunchid

    def save_transfer_groups(self, accounts_mapping: list, transaction_monoid_to_lunchid: dict):
        transfer_mcc = self.configs["mono"]["options"]["transfer_mcc"]
        add_mcc_tag = self.configs["mono"]["options"]["add_mcc_tag"]
        group_max_time_diff_secs = self.configs["lunchmoney"]["options"]["group_max_time_diff_secs"]
        groups = []

        transfer_transactions = []
        for account in accounts_mapping:
            transactions = account["new_account_transactions"]

            transfer_transactions = transfer_transactions + \
                                    [trans for trans in transactions if trans["mcc"] == transfer_mcc]

        logging.info(f"found {len(transfer_transactions)} transfer transactions")

        already_in_group = set()
        for index, tranfer in enumerate(transfer_transactions):
            if index in already_in_group:
                continue
            already_in_group.add(index)
            group_transfers = [gr_tr for gr_tr in transfer_transactions

                               # if time is nearly same, but it is different transaction in list
                               if gr_tr["id"] != tranfer["id"] and
                                  abs(gr_tr["time"] - tranfer["time"]) < group_max_time_diff_secs

                               #and abs(gr_tr["operationAmount"]) == abs(tranfer["operationAmount"])]

                               # and if currency same - amounts should match
                               and abs(gr_tr["operationAmount"]) == abs(tranfer["operationAmount"]) or
                                   abs(gr_tr["operationAmount"]) == abs(tranfer["amount"]) or
                                   abs(gr_tr["amount"]) == abs(tranfer["amount"])]
            if len(group_transfers) > 0:
                [already_in_group.add(transfer_transactions.index(tr)) for tr in group_transfers]
                groups.append([tranfer, *group_transfers])

        logging.info(f"group transfer transactions into {len(groups)} groups")

        for group in groups:
            group_ids = [transaction_monoid_to_lunchid[tr["id"]] for tr in group]
            lunch_group = Mapper.map_transaction_group(
                group[0], group_ids, add_mcc_tag)
            self.lunchmoney_api.create_transaction_group(lunch_group)
        return groups

    @staticmethod
    def __filter_transactions(lunch_acc_transactions, new_mono_transactions):
        external_ids = set([tr["external_id"] for tr in lunch_acc_transactions
                            if tr["external_id"] is not None and len(tr["external_id"]) > 0])

        return [tr for tr in new_mono_transactions
                if tr["id"] not in external_ids]

    @staticmethod
    def __group_transaction_per_date(latest_transactions: list):
        transactions_per_date = {}
        for trans in latest_transactions:
            date_trans_list = transactions_per_date.setdefault(trans["date"], [])
            transaction_external_id = trans["external_id"]
            if transaction_external_id is not None:
                date_trans_list.append(transaction_external_id)
        return transactions_per_date

    def __get_import_params(self, transactions_per_date: dict):
        min_import_start_date = add_days(now(), -1 * self.configs["mono"]["options"]["max_statement_days"]).date()
        if len(transactions_per_date.keys()) == 0:
            default_start_date = datetime.strptime(
                self.configs["mono"]["options"]["default_start_date"],
                "%Y-%m-%d").date()
            start_date = default_start_date if (default_start_date > min_import_start_date) else min_import_start_date

            return start_date, []
        last_transaction_date = max(transactions_per_date.keys())
        same_day_ids = transactions_per_date.get(last_transaction_date)
        start_date = datetime.strptime(last_transaction_date, "%Y-%m-%d").date()
        if len(same_day_ids) == 0:
            start_date = add_days(start_date, 1)
        start_date = start_date if (start_date > min_import_start_date) else min_import_start_date

        return start_date, same_day_ids
