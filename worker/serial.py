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


def read_lines_and_write_db(device):
    try:
        serial_port = device.get("port")
        serial_baud = device.get("baud")
        serial_bit = device.get("bit")
        serial_parity = device.get("parity")
        serial_stopbits = device.get("stopbits")

        bytesize = BYTESIZE_DICT.get(serial_bit, serial.EIGHTBITS)
        parity = PARITY_DICT.get(serial_parity, serial.PARITY_NONE)
        stopbits = STOPBITS_DICT.get(str(serial_stopbits), serial.STOPBITS_ONE)
        
    except Exception:
        log.error(f"{serial_port}: could not read serial .env: {e.args[0]}")
        time.sleep(60)
        read_lines_and_write_db(serial_port)

    if os.environ.get("DEV", "false") == "true":
        while True:
            line = generate_mock_data()
            log.info("got data")
            if line:
                data = parse_data(line)
                write_data(port= serial_port, data=data)
            time.sleep(10)
    try:
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
                    try:
                        data = parse_data(line)
                    except Exception as e:
                        log.error(f"{serial_port}: could not parse data: {e.args[0]}")
                        data = None
                    try:
                        if data is not None:
                            write_data(data=data)
                    except Exception as e:
                        log.error(f"{serial_port}: could not write data: {e.args[0]}")
                    
    except Exception as e:
        log.error(f"{serial_port}: error initializing serial connection: {e.args[0]}")
        time.sleep(60)
        read_lines_and_write_db(serial_port)

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
