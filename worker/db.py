import psycopg2
import logging
import os

log = logging.getLogger("worker.startup")
log.setLevel(logging.INFO)


class DataBaseConnection:
    def __init__(self):
        self.dbname = os.environ.get("DB_DB")
        self.user = os.environ.get("DB_USER")
        self.pwd = os.environ.get("DB_PASSWORD")
        self.host = os.environ.get("DB_HOST")
        self.port = os.environ.get("DB_PORT")

        if None in [self.dbname, self.user, self.pwd, self.host]:
            raise Exception(".env missing necessary information for db connection")

    def __enter__(self):
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.pwd,
            host=self.host,
            port=self.port,
        )

        log.info("connected to db")
        return self.conn.__enter__()
    
    def __exit__(self, type, value, traceback):
        return self.conn.__exit__(type, value, traceback)


def create_table_if_not_exists():
    table_name = os.environ.get("DB_TABLE")

    if table_name is None:
        raise Exception(".env missing table_name")

    with DataBaseConnection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    device VARCHAR(50),
                    timestamp TIMESTAMP,
                    status INTEGER,
                    voltage FLOAT,
                    current FLOAT,
                    power FLOAT,
                    net_voltage FLOAT,
                    net_current FLOAT,
                    net_power FLOAT,
                    temperature INTEGER
                )
            """
            )
            conn.commit()

    log.info(f"table {table_name} created")


def write_data(port, data):
    table_name = os.environ.get("DB_TABLE")

    if table_name is None:
        raise Exception(".env missing table_name")

    with DataBaseConnection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                    INSERT INTO {table_name} (timestamp, device, status, voltage, current, power, net_voltage, net_current, net_power, temperature) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data["timestamp"],
                    port,
                    data["status"],
                    data["voltage"],
                    data["current"],
                    data["power"],
                    data["net_voltage"],
                    data["net_current"],
                    data["net_power"],
                    data["temperature"],
                ),
            )
            conn.commit()

    log.info("data successfully added")
