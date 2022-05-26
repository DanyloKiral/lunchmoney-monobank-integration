from iso4217 import Currency


class Mapper:
    @staticmethod
    def create_accounts_mapping(account_mappings_config, mono_accounts: list, lunch_accounts: list):
        result = []
        # todo: fix n2 complexity
        for name, mono_props in account_mappings_config.items():
            lunch_acc = Mapper.__select_lunch_acc(lunch_accounts, name)
            mono_acc = Mapper.__select_mono_acc(mono_accounts, mono_props.get('currency'), mono_props.get('type'))
            result.append({
                'lunch_acc': lunch_acc,
                'mono_acc': mono_acc
            })
        return result

    @staticmethod
    def __select_lunch_acc(lunch_accounts, name):
        lunch_acc_search = [acc for acc in lunch_accounts if acc.get('name') == name]
        assert len(lunch_acc_search) == 1, f'Only one Lunchmoney account should have name {name}'
        return lunch_acc_search[0]

    @staticmethod
    def __select_mono_acc(mono_accounts, currency, type):
        iso_curr_code = Currency[currency].number
        mono_acc_search = [acc for acc in mono_accounts
                           if acc.get('currencyCode') == iso_curr_code
                           and acc.get('type') == type]
        assert len(mono_acc_search) == 1, f'Only one Mono account should have type {type} and currency {currency}'
        return mono_acc_search[0]
