import requests

class FireflyImporterApi:
    def __init__(self, configs, credentials):
        self.base_url = configs.get("auto_import_url")
        self.folder = configs.get("folder")
        self.secret = credentials.get('secret')

    def trigger_auto_import_from_folder(self):
        response = requests.post(self.base_url + '/autoimport', params={
            "directory": f"{self.folder}",
            "secret": self.secret
        })
        result = response.json()
        assert response.ok, f"FireflyImporterApi trigger_auto_import_from_folder error: {response.json()}"

    def auto_upload(self, data_file, json_config):
        response = requests.post(
            self.base_url + '/autoupload', 
            params={
                "secret": self.secret
            }, 
            files={
                "importable": open(data_file, "rb"),
                "json": open(json_config, "rb")
            })
        assert response.ok, f"FireflyImporterApi auto_upload error: {response.json()}"
