from flow import ImportFlow
from utils import load_credentials, load_configs, now
import logging


def main():
    logging.basicConfig(
        filename=f"logs/logs-{str(now())}.log",
        format="%(asctime)s %(name)s:%(levelname)s - %(message)s",
        level=logging.DEBUG
    )
    logging.info("app started")

    try:
        configs = load_configs()
        credentials = load_credentials()
        logging.info("loaded configs")

        flow = ImportFlow(configs, credentials)
        flow.run_import()

        logging.info("successfully finished")
    except Exception as e:
        logging.error("Something went wrong", exc_info=True)
    finally:
        logging.info("fin")


if __name__ == "__main__":
    main()
