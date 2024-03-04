import logging
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from worker.db import create_table_if_not_exists
from worker.serial import read_lines_and_write_db
import concurrent.futures


def load_devices():
    file = os.path.join(str(Path(__file__).parent.parent), "devices.json")
    with open(file) as data:
        json_data = json.load(data)
    return json_data.get("devices")


def main():
    devices = load_devices()
    create_table_if_not_exists()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for device in devices:
            executor.submit(read_lines_and_write_db, device)


if __name__ == "__main__":
    log = logging.getLogger("worker.run")
    log.setLevel(logging.INFO)

    log.info("init logger")

    load_dotenv(override=True)

    if os.environ.get("WORKER_BUILD", None) != "OK":
        raise Exception(".env could not be loaded")

    log.info("loaded .env")

    main()
