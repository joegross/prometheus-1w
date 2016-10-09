#!/usr/bin/python

import argparse
import logging
from prometheus_client import start_http_server, Gauge
import time
from w1thermsensor import W1ThermSensor

logger = logging.getLogger(__name__)

class SensorGauge(object):
    def __init__(self, sensor):
        self.sensor = sensor
        self.gauge = Gauge('temp_sensor_%s' % sensor.id, 'DS18B20 sensor temp (F)')

    def post_temp(self):
        temp = self.sensor.get_temperature(W1ThermSensor.DEGREES_F)
        logging.info("Sensor %s has temperature %.2f" % (self.sensor.id, temp))
        self.gauge.set(temp)

class sensor_server(object):
    def __init__(self, sleep=5):
        self.sensors = {}
        for sensor in W1ThermSensor.get_available_sensors():
            self.sensors[sensor.id] = SensorGauge(sensor)
        self.sleep = sleep
        
    def serve_forever(self):
        start_http_server(8000)
        while True:
            for sensor in self.sensors.values():
                sensor.post_temp()
            logging.info("sleeping %s..." % self.sleep)
            time.sleep(self.sleep)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    sensor_server().serve_forever()
