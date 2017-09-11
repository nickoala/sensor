from sensor.DS18B20 import DS18B20

ds = DS18B20('28-00000736781c')

print(ds.temperature().C)

"""
In configuration.yaml:::::

sensor:
  - platform: command_line
    name: DS18B20 Sensor
    command: python3 /path/to/temperature.py
    value_template: '{{ value | round(1) }}'
    unit_of_measurement: "°C"
    scan_interval: 3
"""
