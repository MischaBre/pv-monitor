import time
import datetime
from worker.startup import startup



if __name__ == "__main__":
    startup()
    while True:
        print(f"{datetime.datetime.now()}: run")
        time.sleep(1)