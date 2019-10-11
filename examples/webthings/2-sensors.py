from webthing import Thing, Property, Value, MultipleThings, WebThingServer
import logging
import tornado.ioloop
from sensor import DS18B20, SHT20


def run_server():
    ds18 = DS18B20('28-03199779f5a1')
    ds18_celsius = Value(ds18.temperature().C)

    ds18_thing = Thing(
        'urn:dev:ops:temperature-sensor',
        'Temperature Sensor',
        ['TemperatureSensor'])

    ds18_thing.add_property(
        Property(
            ds18_thing,
            'celsius',
            ds18_celsius,
            metadata={
                '@type': 'TemperatureProperty',
                'title': 'Celsius',
                'type': 'number',
                'unit': '°C',
                'readOnly': True }))

    sht = SHT20(1, 0x40)
    h, t = sht.all()
    sht_celsius = Value(t.C)
    sht_rh = Value(h.RH)

    sht_thing = Thing(
        'urn:dev:ops:humidity-temperature-sensor',
        'Humidity & Temperature Sensor',
        ['MultiLevelSensor', 'TemperatureSensor'])

    # If you want icon to show humidity:
    #   - remove type `TemperatureSensor`, and
    #   - change temperature metadata @type to `LevelProperty`

    sht_thing.add_property(
        Property(
            sht_thing,
            'humidity',
            sht_rh,
            metadata={
                '@type': 'LevelProperty',
                'title': 'Relative humidity',
                'unit': 'percent',
                'readOnly': True }))

    sht_thing.add_property(
        Property(
            sht_thing,
            'temperature',
            sht_celsius,
            metadata={
                '@type': 'TemperatureProperty',
                'title': 'Celsius',
                'unit': '°C',
                'readOnly': True }))

    server = WebThingServer(
                MultipleThings([ds18_thing, sht_thing], 'Multi-sensor Device'),
                port=8888)

    def update_values():
        t = ds18.temperature()
        ds18_celsius.notify_of_external_update(t.C)

        h, t = sht.all()
        sht_celsius.notify_of_external_update(t.C)
        sht_rh.notify_of_external_update(h.RH)

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
