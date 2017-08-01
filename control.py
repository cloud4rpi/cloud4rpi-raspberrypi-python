# -*- coding: utf-8 -*-
#
# Cloud4RPi Example for Raspberry Pi
# ==================================
#
# This example demonstrates different scenarios of using Cloud4RPi service
# on Raspberry Pi:
#
# - Monitoring events
# - Controling a GPIO pin
# - Monitoring temperature with the DS18B20 sensor
#
# For complete instructions on how to run this example, refer
# to the [How To](https://cloud4rpi.github.io/docs/howto/) article.
#
# The DS18B20 sensor should be connected as follows:
#
#  / GND |────────────> GND
# | DATA |─────────┬──> GPIO4
#  \ VCC |─┬─[4k7]─┘
#          └──────────> 5V
#  DS18B20 (bottom view)

from os import uname
from socket import gethostname
import sys
import time
import random
import RPi.GPIO as GPIO  # pylint: disable=F0401
import cloud4rpi
import ds18b20
import rpi

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'

# Constants
LED_PIN = 12
DATA_SENDING_INTERVAL = 30  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.5  # 500 ms

# configure GPIO library
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)


# handler for the button or switch variable
def led_control(value=None):
    GPIO.output(LED_PIN, value)
    return GPIO.input(LED_PIN)


def listen_for_events():
    # write your own logic here
    result = random.randint(1, 5)
    if result == 1:
        return 'RING'

    if result == 5:
        return 'BOOM!'

    return 'IDLE'


def main():
    # load w1 modules
    ds18b20.init_w1()

    # detect ds18b20 temperature sensors
    ds_sensors = ds18b20.DS18b20.find_all()

    # Put variable declarations here
    variables = {
        'Room Temp': {
            'type': 'numeric',
            'bind': ds_sensors[0] if ds_sensors else None
        },
        # 'Outside Temp': {
        #     'type': 'numeric',
        #     'bind': ds_sensors[1] if len(ds_sensors) > 1 else None
        # },
        'LED On': {
            'type': 'bool',
            'value': False,
            'bind': led_control
        },
        'CPU Temp': {
            'type': 'numeric',
            'bind': rpi.cpu_temp
        },
        'STATUS': {
            'type': 'string',
            'bind': listen_for_events
        }

    }

    diagnostics = {
        'CPU Temp': rpi.cpu_temp,
        'IP Address': rpi.ip_address,
        'Host': gethostname(),
        'Operating System': " ".join(uname())
    }

    device = cloud4rpi.connect(DEVICE_TOKEN)
    device.declare(variables)
    device.declare_diag(diagnostics)

    device.publish_config()

    # Adds a 1 second delay to ensure device variables are created
    time.sleep(1)

    try:
        data_timer = 0
        diag_timer = 0
        while True:
            if data_timer <= 0:
                device.publish_data()
                data_timer = DATA_SENDING_INTERVAL

            if diag_timer <= 0:
                device.publish_diag()
                diag_timer = DIAG_SENDING_INTERVAL

            time.sleep(POLL_INTERVAL)
            diag_timer -= POLL_INTERVAL
            data_timer -= POLL_INTERVAL

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
