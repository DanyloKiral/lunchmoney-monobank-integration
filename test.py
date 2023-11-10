from datetime import datetime
from firefly_api import FireflyImporterApi
from firefly_api.firefly_api import FireflyApi
from mono_api.mono_api import MonoApi
from utils.files import load_configs, load_credentials

def main():
    configs = load_configs()
    credentials = load_credentials()

    firefly_api = FireflyApi(configs["firefly"], credentials["firefly"])
    firefly_api.insert_transactions([
        {
                "order": 0,
                "external_id": "r34f34g45geg",
                "type": "withdrawal",
                "date": "2023-11-04",
                "description": "test",

                "amount": 20,
                #"foreign_currency_code": mono_trans_currency_code if trans_has_diff_currency else None,
                #"foreign_amount": mono_trans["operationAmount"] / 100 if trans_has_diff_currency else None,
                "currency_code": "UAH",

                #"source_id": firefly_account["id"] if trans_is_withdrawal else None,
                "destination_name": "test",

                "source_name": "Mono Black",
                #"destination_id": firefly_account["id"] if not trans_is_withdrawal else None,
                #"notes": "",
                "tags": ["test"]
            }
    ])

    importer_api = FireflyImporterApi(configs["firefly-importer"], credentials["firefly-importer"])
    client_info = importer_api.trigger_auto_import_from_folder()
    result = client_info





if __name__ == "__main__":
    main()
