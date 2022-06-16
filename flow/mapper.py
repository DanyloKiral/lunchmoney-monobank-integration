import iso18245

from iso4217 import Currency
from utils import unix_to_datetime


class Mapper:
    @staticmethod
    def create_accounts_mapping(account_mappings_config, mono_client_info: dict, lunch_accounts: list):
        mono_accounts = mono_client_info["accounts"]
        mono_jars = mono_client_info["jars"]
        result = []
        # todo: fix n2 complexity
        for name, mono_props in account_mappings_config.items():
            lunch_acc = Mapper.__select_lunch_acc(lunch_accounts, name)
            if mono_props["type"] == "jar":
                mono_acc = Mapper.__select_mono_jar(mono_jars, mono_props["jar_name"])
            else:
                mono_acc = Mapper.__select_mono_acc(mono_accounts, mono_props.get("currency"), mono_props.get("type"))
            result.append({
                "lunch_acc": lunch_acc,
                "mono_acc": mono_acc
            })
        return result

    @staticmethod
    def map_to_lunch_transactions(mono_transactions, lunch_account, add_mcc_tag):
        result = []
        for mono_trans in mono_transactions:
            # todo: handle category, mcc parsing
            # todo: check balance?

            # note: mono transaction can have "comment", if it is transfer
            lunch_trans = {
                "date": unix_to_datetime(mono_trans["time"]).strftime("%Y-%m-%d"),
                "amount": mono_trans["amount"] / 100,
                # "category_id": "", # ???
                "payee": mono_trans["description"][:140],
                "currency": lunch_account["currency"],
                "asset_id": lunch_account["id"],
                # "recurring_id": "",
                "notes": "",
                # "status": "",
                "external_id": Mapper.generate_external_id(mono_trans),
                "tags": Mapper.__get_tags_for_mono_transaction(mono_trans, add_mcc_tag)
            }
            result.append(lunch_trans)
        return result

    @staticmethod
    def map_transaction_group(any_group_transaction, transaction_ids, add_mcc_tag):
        return {
            "date": unix_to_datetime(any_group_transaction["time"]).strftime("%Y-%m-%d"),
            "payee": "Mono transfer",
            # "category_id": "",
            # "notes": "",
            "tags": Mapper.__get_tags_for_mono_transaction(any_group_transaction, add_mcc_tag),
            "transactions": transaction_ids
        }

    @staticmethod
    def generate_external_id(mono_transaction):
        return f'{mono_transaction["time"]}_{mono_transaction["amount"]}'

    @staticmethod
    def __select_lunch_acc(lunch_accounts, name):
        lunch_acc_search = [acc for acc in lunch_accounts if acc["name"] == name]
        assert len(lunch_acc_search) == 1, f"Only one Lunchmoney account should have name {name}"
        return lunch_acc_search[0]

    @staticmethod
    def __select_mono_acc(mono_accounts, currency, acc_type):
        iso_curr_code = Currency[currency].number
        mono_acc_search = [acc for acc in mono_accounts
                           if acc["currencyCode"] == iso_curr_code
                           and acc["type"] == acc_type]
        assert len(mono_acc_search) == 1, f"Only one Mono account should have type {acc_type} and currency {currency}"
        return mono_acc_search[0]

    @staticmethod
    def __select_mono_jar(mono_jars, jar_name):
        mono_jar_search = [jar for jar in mono_jars
                           if jar["title"] == jar_name]
        assert len(mono_jar_search) == 1, f"Only one Mono jar should have name {jar_name}"
        return mono_jar_search[0]

    @staticmethod
    def __get_tags_for_mono_transaction(trans, add_mcc_tag):
        tags = ["Monobank integration"]
        if add_mcc_tag:
            mcc = iso18245.get_mcc(str(trans["mcc"]))
            tags.append(mcc.iso_description if len(mcc.iso_description) > 0 else mcc.usda_description)
        return tags
