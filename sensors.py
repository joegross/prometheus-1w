#!/usr/bin/python

import argparse
import logging
from prometheus_client import start_http_server, Gauge
import time
from w1thermsensor import W1ThermSensor

logger = logging.getLogger(__name__)

class sensor_server(object):
    def __init__(self, sleep=5):
        self.sensors = {}
        self.sleep = sleep
        start_http_server(8000)
        self.gauge = Gauge('sensor_temp_degF', 'DS18B20 sensor temp (F)', ['id'])
        
    def serve_forever(self):
        while True:
            for sensor in W1ThermSensor.get_available_sensors():
                temp = sensor.get_temperature(W1ThermSensor.DEGREES_F)
                logging.info("Sensor %s has temperature %.2f" % (sensor.id, temp))
                self.gauge.labels(id=sensor.id).set(temp)
            logging.info("sleeping %s..." % self.sleep)
            time.sleep(self.sleep)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    sensor_server().serve_forever()
