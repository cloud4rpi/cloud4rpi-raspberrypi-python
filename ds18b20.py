# -*- coding: utf-8 -*-

import os
import re
import subprocess

W1_DEVICES = '/sys/bus/w1/devices/'
W1_SENSOR_PATTERN = re.compile('(10|22|28)-.+', re.IGNORECASE)


def modprobe(module):
    return subprocess.check_call(['modprobe', module])


def init_w1():
    modprobe('w1-gpio')
    modprobe('w1-therm')


def is_w1_sensor(path):
    return \
        W1_SENSOR_PATTERN.match(path) and \
        os.path.isfile(sensor_full_path(path))


def sensor_full_path(sensor):
    return os.path.join(W1_DEVICES, sensor, 'w1_slave')


def read_whole_file(path):
    with open(path, 'r') as f:
        return f.read()


class InvalidW1Address(Exception):
    def __init__(self, address):
        super(InvalidW1Address, self).__init__()
        self.address = address


def guard_against_invalid_address(address):
    if not W1_SENSOR_PATTERN.match(address):
        raise InvalidW1Address(address)


class DS18b20(object):
    @staticmethod
    def find_all():
        return [DS18b20(x)
                for x in sorted(os.listdir(W1_DEVICES)) if is_w1_sensor(x)]

    def __init__(self, address):
        guard_against_invalid_address(address)
        self.address = address

    def read(self):
        readings = read_whole_file(sensor_full_path(self.address))
        temp_token = 't='
        temp_index = readings.find(temp_token)
        if temp_index < 0:
            return None
        temp = readings[temp_index + len(temp_token):]
        return float(temp) / 1000
