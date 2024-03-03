import os
import serial
import logging
import time
from datetime import datetime
from worker.db import write_data

log = logging.getLogger("worker.serial")
log.setLevel(logging.INFO)


BYTESIZE_DICT = {
    5: serial.FIVEBITS,
    6: serial.SIXBITS,
    7: serial.SEVENBITS,
    8: serial.EIGHTBITS,
}

PARITY_DICT = {
    "none": serial.PARITY_NONE,
    "even": serial.PARITY_EVEN,
    "odd": serial.PARITY_ODD,
    "mark": serial.PARITY_MARK,
    "names": serial.PARITY_NAMES,
    "space": serial.PARITY_SPACE,
}

STOPBITS_DICT = {
    "1": serial.STOPBITS_ONE,
    "1.5": serial.STOPBITS_ONE_POINT_FIVE,
    "2": serial.STOPBITS_TWO,
}


def parse_data(data):
    # Split the data by whitespace
    values = data.split()

    # Extracting individual values
    (
        date_str,
        time_str,
        status,
        voltage,
        current,
        power,
        net_voltage,
        net_current,
        net_power,
        temperature,
    ) = values

    # Convert date and time strings to datetime object
    timestamp = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M:%S")

    return {
        "timestamp": timestamp,
        "status": int(status),
        "voltage": float(voltage),
        "current": float(current),
        "power": float(power),
        "net_voltage": float(net_voltage),
        "net_current": float(net_current),
        "net_power": float(net_power),
        "temperature": int(temperature),
    }


def read_lines_and_write_db():
    serial_port = os.environ.get("SERIAL_PORT")
    serial_baud = os.environ.get("SERIAL_BAUD")
    serial_bit = os.environ.get("SERIAL_BIT")
    serial_parity = os.environ.get("SERIAL_PARITY")
    serial_stopbits = os.environ.get("SERIAL_STOPBITS")

    bytesize = BYTESIZE_DICT.get(serial_bit, serial.EIGHTBITS)
    parity = PARITY_DICT.get(serial_parity, serial.PARITY_NONE)
    stopbits = STOPBITS_DICT.get(str(serial_stopbits), serial.STOPBITS_ONE)

    if os.environ.get("DEV", "false") == "true":
        while True:
            line = generate_mock_data()
            log.info("got data")
            if line:
                data = parse_data(line)
                write_data(data=data)
            time.sleep(10)

    with serial.Serial(
        port=serial_port,
        baudrate=serial_baud,
        parity=parity,
        bytesize=bytesize,
        stopbits=stopbits,
    ) as ser:
        while True:
            line = ser.readline().strip().decode("utf-8")
            log.info("got data")
            if line:
                data = parse_data(line)
                write_data(data=data)


import random


def generate_mock_data():
    date_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    status = random.randint(0, 1)
    voltage = round(random.uniform(200, 400), 2)
    current = round(random.uniform(0, 5), 2)
    power = round(voltage * current, 2)
    net_voltage = round(random.uniform(200, 400), 2)
    net_current = round(random.uniform(0, 5), 2)
    net_power = round(net_voltage * net_current, 2)
    temperature = random.randint(20, 40)

    return f"{date_time} {status} {voltage} {current} {power} {net_voltage} {net_current} {net_power} {temperature}"
