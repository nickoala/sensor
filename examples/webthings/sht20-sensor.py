from webthing import Thing, Property, Value, SingleThing, WebThingServer
import logging
import tornado.ioloop
from sensor import SHT20


def run_server():
    sht = SHT20(1, 0x40)
    h, t = sht.all()
    celsius = Value(t.C)
    humidity = Value(h.RH)

    thing = Thing(
        'urn:dev:ops:humidity-temperature-sensor',
        'SHT20',
        ['MultiLevelSensor'])

    thing.add_property(
        Property(
            thing,
            'humidity',
            humidity,
            metadata={
                '@type': 'LevelProperty',
                'title': 'Humidity',
                'type': 'number',
                'unit': 'percent',
                'readOnly': True }))

    thing.add_property(
        Property(
            thing,
            'temperature',
            celsius,
            metadata={
                '@type': 'LevelProperty',
                'title': 'Temperature',
                'type': 'number',
                'unit': '°C',
                'readOnly': True }))

    server = WebThingServer(SingleThing(thing), port=8889)

    def update():
        h, t = sht.all()
        celsius.notify_of_external_update(t.C)
        humidity.notify_of_external_update(h.RH)

    timer = tornado.ioloop.PeriodicCallback(update, 3000)
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
