import logging
import os
from dotenv import load_dotenv
from worker.db import create_table_if_not_exists
from worker.serial import read_lines_and_write_db


def main():
    create_table_if_not_exists()
    read_lines_and_write_db()


if __name__ == "__main__":
    log = logging.getLogger("worker.run")
    log.setLevel(logging.INFO)

    log.info("init logger")

    load_dotenv()
    
    if os.environ.get("WORKER_BUILD", None) != "OK":
        raise Exception(".env could not be loaded")
    
    log.info("loaded .env")


    main()
