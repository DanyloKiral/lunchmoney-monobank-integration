import json


def load_configs():
    return __load_json("config.json")


def load_credentials():
    return __load_json("credentials.json")


def save_to_json_file(obj, filename):
    with open(filename, "w") as fp:
        json.dump(obj, fp, ensure_ascii=False)


def __load_json(file_name):
    file = open(file_name)
    config = json.load(file)
    file.close()

    return config
