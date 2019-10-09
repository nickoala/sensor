from webthing import Property, Thing, Value, MultipleThings, WebThingServer
import logging
import tornado.ioloop
from sensor import DS18B20, SHT20


class TemperatureSensor(Thing):
    def __init__(self, address):
        Thing.__init__(
            self,
            'urn:dev:ops:temperature-sensor',
            'Temperature Sensor',
            ['TemperatureSensor'],
        )

        self.sensor = DS18B20(address)

        self.temperature = Value(self.read_celsius())
        self.add_property(
            Property(self,
                     'temperature',
                     self.temperature,
                     metadata={
                         '@type': 'TemperatureProperty',
                         'title': 'Temperature',
                         'type': 'number',
                         'description': 'The current temperature in °C',
                         'minimum': -50,
                         'maximum': 70,
                         'unit': '°C',
                         'readOnly': True,
                     }))

        logging.debug('starting the sensor update looping task')
        self.timer = tornado.ioloop.PeriodicCallback(
            self.update,
            3000
        )
        self.timer.start()

    def update(self):
        c = self.read_celsius()
        logging.debug('setting new temperature: %s', c)
        self.temperature.notify_of_external_update(c)

    def cancel_update_task(self):
        self.timer.stop()

    def read_celsius(self):
        return self.sensor.temperature().C


class HumidityTemperatureSensor(Thing):
    def __init__(self, bus, address):
        Thing.__init__(
            self,
            'urn:dev:ops:humidity-temperature-sensor',
            'Humidity+Temperature Sensor',
            ['MultiLevelSensor', 'TemperatureSensor'],
        )

        # If you want icon to show humidity:
        #   - remove type `TemperatureSensor`, and
        #   - change temperature property @type to `LevelProperty`

        self.sensor = SHT20(bus, address)

        self.humidity = Value(self.sensor.humidity().RH)
        self.add_property(
            Property(self,
                     'humidity',
                     self.humidity,
                     metadata={
                         '@type': 'LevelProperty',
                         'title': 'Humidity',
                         'unit': 'percent',
                         'readOnly': True,
                     }))

        self.temperature = Value(self.sensor.temperature().C)
        self.add_property(
            Property(self,
                     'temperature',
                     self.temperature,
                     metadata={
                         '@type': 'TemperatureProperty',
                         'title': 'Temperature',
                         'unit': '°C',
                         'readOnly': True,
                     }))

        logging.debug('starting the sensor update looping task')
        self.timer = tornado.ioloop.PeriodicCallback(
            self.update,
            3000
        )
        self.timer.start()

    def update(self):
        rh, celsius = self.read_numbers()
        logging.debug('setting new humidity & temperature: %s, %s', rh, celsius)
        self.humidity.notify_of_external_update(rh)
        self.temperature.notify_of_external_update(celsius)

    def cancel_update_task(self):
        self.timer.stop()

    def read_numbers(self):
        h,t = self.sensor.all()
        return h.RH, t.C


def run_server():
    t_sensor = TemperatureSensor('28-031997791364')
    ht_sensor = HumidityTemperatureSensor(1, 0x40)

    server = WebThingServer(
                MultipleThings([t_sensor, ht_sensor], 'Multi-sensor Device'),
                port=8888)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.debug('canceling the sensor update looping task')
        t_sensor.cancel_update_task()
        ht_sensor.cancel_update_task()
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()
