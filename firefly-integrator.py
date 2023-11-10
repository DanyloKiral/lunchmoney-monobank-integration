from firefly_flow import ImportFlow
from utils import load_credentials, load_configs, now, load_json
import logging

import sys, argparse

def main():
    try:
        parser=argparse.ArgumentParser()
        parser.add_argument("--config", help="Path to config json file", default="config.json")
        parser.add_argument("--credentials", help="Path to json file with credentials", default="credentials.json")
        args=parser.parse_args()

        configs = load_json(args.config)
        credentials = load_json(args.credentials)

        logs_folder = configs.get("logs").get("logs_folder")
        logging.basicConfig(
            filename=f"{logs_folder}/firefly-logs-{now().strftime('%Y-%m-%dT%H:%M')}.log",
            format="%(asctime)s %(name)s:%(levelname)s - %(message)s",
            level=logging.DEBUG
        )
        logging.info(f"app started. loaded configs/credentials from {args.config} / {args.credentials}")

        flow = ImportFlow(configs, credentials)
        flow.run_import()

        logging.info("successfully finished")
    except Exception as e:
        logging.error("Something went wrong", exc_info=True)
        print(f"Something went wrong. Exception = {e}")
    finally:
        logging.info("fin")


if __name__ == "__main__":
    main()
