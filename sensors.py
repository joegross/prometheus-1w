#!/usr/bin/python

import argparse
from collections import deque
import logging
from prometheus_client import start_http_server, Gauge
import time
# import w1thermsensor.W1ThermSensor
from w1thermsensor import W1ThermSensor
import w1thermsensor.core

logger = logging.getLogger(__name__)

class moving_average(object):
    def __init__(self, maxsize=10):
        self.maxsize = maxsize
        self.queue = deque()

    def append(self, value):
        self.queue.append(value)
        while len(self.queue) > self.maxsize:
            self.queue.popleft()

    def average(self):
        return float(sum(self.queue)) / (len(self.queue) + 1)
        

class sensor_server(object):
    def __init__(self, sleep=5):
        self.sleep = sleep
        start_http_server(8000)
        self.gauge = Gauge('sensor_temp_degF', 'DS18B20 sensor temp (F)', ['id'])
        # blacklist erronous values
        self.absurd_temps = [
            185.,
        ]
        
    def serve_forever(self):
        while True:
            for sensor in w1thermsensor.W1ThermSensor.get_available_sensors():
                try:
                    temp = sensor.get_temperature(W1ThermSensor.DEGREES_F)
                except w1thermsensor.core.SensorNotReadyError as e:
                    logging.warning("Sensor %s not ready: %s" % (sensor.id, e))
                    continue
                logging.info("Sensor %s has temperature %.2f" % (sensor.id, temp))
                if temp in self.absurd_temps:
                    logging.warning("Sensor %s value: %s absurd. Not posting" % (sensor.id, temp))
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
