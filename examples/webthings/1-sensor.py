from webthing import Property, Thing, Value, SingleThing, WebThingServer
import logging
import tornado.ioloop
from sensor import DS18B20


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


def run_server():
    thing = TemperatureSensor('28-031997791364')

    server = WebThingServer(SingleThing(thing), port=8888)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.debug('canceling the sensor update looping task')
        thing.cancel_update_task()
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()
