import json
import csv
import os
import shutil

def load_configs():
    return __load_json("config.json")


def load_credentials():
    return __load_json("credentials.json")


def save_to_json_file(obj, filename):
    with open(filename, "w") as fp:
        json.dump(obj, fp, ensure_ascii=False)

def save_list_to_csv_file(rows: list[dict], filename):
    if len(rows) < 1:
        return
    headers = list(rows[0].keys())
    with open(filename, "w") as fp:
        writer = csv.DictWriter(fp, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

def remove_file_if_exists(filename):
    try:
        os.remove(filename)
    except OSError:
        pass

def copy_file(src, dst):
    shutil.copyfile(src, dst)

def __load_json(file_name):
    file = open(file_name)
    config = json.load(file)
    file.close()

    return config
