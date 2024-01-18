
import logging
import iso18245
from iso4217 import Currency

from utils.datetime import unix_to_datetime


class Mapper:
    @staticmethod
    def create_accounts_mapping(account_mappings_config, mono_client_info: dict, firefly_accounts: list):
        mono_accounts = mono_client_info["accounts"]
        mono_jars = mono_client_info["jars"] if "jars" in mono_client_info else []
        result = []
        # todo: fix n2 complexity
        for name, mono_props in account_mappings_config.items():
            lunch_acc = Mapper.__select_firefly_acc(firefly_accounts, name)
            if mono_props["type"] == "jar":
                mono_acc = Mapper.__select_mono_jar(mono_jars, mono_props["jar_name"])
            else:
                mono_acc = Mapper.__select_mono_acc(mono_accounts, mono_props.get("currency"), mono_props.get("type"))
            result.append({
                "firefly_acc": lunch_acc,
                "mono_acc": mono_acc
            })
        return result
    

    @staticmethod
    def __select_firefly_acc(firefly_accounts, name):
        firefly_acc_search = [acc for acc in firefly_accounts if acc["name"] == name]
        assert len(firefly_acc_search) == 1, f"Only one Firefly account should have name {name}"
        return firefly_acc_search[0]

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
    def map_to_firefly_transactions(mono_transactions, firefly_account, add_mcc_tag):
        result = []
        for mono_trans in mono_transactions:
            # todo: handle category, mcc parsing
            # todo: check balance?

            # note: mono transaction can have "comment", if it is transfer
            mono_trans_currency_code = [c for c in Currency if c.number == mono_trans["currencyCode"]][0].code
            trans_has_diff_currency = mono_trans_currency_code.upper() != firefly_account["currency"].upper()
            trans_is_withdrawal = mono_trans["amount"] <= 0
            firefly_trans = {
                "order": 0,
                "external_id": mono_trans["id"],
                "type": "withdrawal" if trans_is_withdrawal else "deposit",
                "date": unix_to_datetime(mono_trans["time"]).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "description": mono_trans["description"],

                "amount": abs(mono_trans["amount"] / 100),
                "currency_code": firefly_account["currency"],

                #"notes": "",
                "tags": Mapper.__get_tags_for_mono_transaction(mono_trans, add_mcc_tag)
            }

            if (trans_is_withdrawal):
                firefly_trans["source_id"] = firefly_account["id"]
                firefly_trans["destination_name"] = mono_trans["description"]
            else:
                firefly_trans["source_name"] = mono_trans["description"]
                firefly_trans["destination_id"] = firefly_account["id"]

            if (trans_has_diff_currency):
                firefly_trans["foreign_currency_code"] = mono_trans_currency_code
                firefly_trans["foreign_amount"] = abs(mono_trans["operationAmount"] / 100)

            result.append(firefly_trans)
        return result
    
    @staticmethod
    def __get_tags_for_mono_transaction(trans, add_mcc_tag):
        tags = ["mono-integration"]
        tr_mcc = str(trans["mcc"])
        if add_mcc_tag and len(tr_mcc) > 0 and iso18245.validate_mcc(tr_mcc):
            try:
                mcc = iso18245.get_mcc(tr_mcc)
                item = mcc.iso_description if len(mcc.iso_description) > 0 else mcc.usda_description
                if len(item) == 0:
                    item = tr_mcc
                tags.append(item)
            except iso18245.MCCNotFound:
                logging.exception(f'MCC not found error. mcc = {tr_mcc}')
        return tags