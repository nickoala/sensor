from webthing import Thing, Property, Value, SingleThing, WebThingServer
import logging
import tornado.ioloop
from sensor import DS18B20


def run_server():
    ds18 = DS18B20('28-03199779f5a1')
    celsius = Value(ds18.temperature().C)

    thing = Thing(
        'urn:dev:ops:temperature-sensor',
        'Temperature Sensor',
        ['TemperatureSensor'])

    thing.add_property(
        Property(
            thing,
            'celsius',
            celsius,
            metadata={
                '@type': 'TemperatureProperty',
                'title': 'Celsius',
                'type': 'number',
                'unit': '°C',
                'readOnly': True }))

    server = WebThingServer(SingleThing(thing), port=8888)

    def update_values():
        t = ds18.temperature()
        celsius.notify_of_external_update(t.C)

    timer = tornado.ioloop.PeriodicCallback(update_values, 3000)
    timer.start()

    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.debug('stopping update task')
        timer.stop()
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()
