# Raspberry Pi Sensors

This is a **Python 3** package that enables **Raspberry Pi** to read various
sensors.

Supported devices include:
- **DS18B20** temperature sensor
- **BMP180** pressure and temperature sensor
- **HTU21D** humidity and temperature sensor
- **SHT20** humidity and temperature sensor
- **MCP3004** A/D Converter (**MCP3008** also compatible)

The chief motivation for this package is educational. I am teaching a Raspberry
Pi course, and find it very troublesome for students having to download a
separate library every time they use another sensor. With this package, download
once and they are set (for my course, anyway). I hope you find it useful, too.

## Installation

It is best to update Linux first.

`sudo apt-get update`  
`sudo apt-get dist-upgrade`

Install this package:

`sudo pip3 install sensor`

But the `sensor` package would not work by itself. Communicating with sensors
often requires some sort of serial protocol, such as **1-wire**, **I2C**, or
**SPI**. You have to know which sensor speaks which, and set up Raspberry Pi to
do so.

## Enable 1-Wire, I2C, or SPI

`sudo raspi-config`, enter **Interfacing Options**, enable the protocols you
need.

## Know your sensor's address

Unlike many libraries out there, this library knows **no default bus number**
and **no default device address**. I want learners to be explicitly aware of
those numbers, even if they are fixed.

For example:
- **I2C** bus is numbered **1**
- **SPI** bus is numbered **0**

To find out individual sensor's address:
- For 1-wire sensors, go to `/sys/bus/w1/devices/`
- For I2C sensors, use `i2cdetect -y 1`
- For SPI sensors, you should know which CS pin you use

## My sensors don't give simple numbers

Unlike many libraries out there, this library does not return a simple Celcius
degree when reading temperatures, does not return a simple hPa value when
reading pressure, does not return a simple RH% when reading humidity, etc.
Instead, I return a **namedtuple** representing the quantity, which offers two
benefits:

- No more conversion needed. Suppose you get a *Temperature* called `t`, you may
  access the Celcius degree by `t.C` as easily as you do Fahrenheit by `t.F`.
- Namedtuples may have methods. For example, a *Pressure* has a method called
  `altitude()`, which tells you how high you are above mean sea level.

## DS18B20

- Temperature, 1-wire
- To find out the sensor's address:

    ```
    $ cd /sys/bus/w1/devices/
    $ ls
    28-XXXXXXXXXXXX  w1_bus_master1
    ```

Read the sensor as follows:

```python
from sensor import DS18B20

ds = DS18B20('28-XXXXXXXXXXXX')
t = ds.temperature()  # read temperature

print(t)    # this is a namedtuple
print(t.C)  # Celcius
print(t.F)  # Fahrenheit
print(t.K)  # Kelvin
```

## BMP180

- Pressure + Temperature, I2C
- Use `i2cdetect -y 1` to check address. It is probably `0x77`.

```python
from sensor import BMP180

# I2C bus=1, Address=0x77
bmp = BMP180(1, 0x77)

p = bmp.pressure()  # read pressure
print(p)            # namedtuple
print(p.hPa)        # hPa value

t = bmp.temperature()  # read temperature
print(t)               # namedtuple
print(t.C)             # Celcius degree

p, t = bmp.all()  # read both at once
print(p)          # Pressure namedtuple
print(t)          # Temperature namedtuple

# Look up mean sea level pressure from local observatory.
# 1009.1 hPa is only for example.
a = p.altitude(msl=1009.1)

print(a)     # Altitude
print(a.m)   # in metre
print(a.ft)  # in feet
```

## HTU21D

- Humidity + Temperature, I2C
- Use `i2cdetect -y 1` to check address. It is probably `0x40`.

```python
from sensor import HTU21D

# I2C bus=1, Address=0x40
htu = HTU21D(1, 0x40)

h = htu.humidity()  # read humidity
print(h)            # namedtuple
print(h.RH)         # relative humidity

t = htu.temperature()  # read temperature
print(t)               # namedtuple
print(t.F)             # Fahrenheit

h, t = htu.all()  # read both at once
```

## SHT20

- Humidity + Temperature, I2C
- Use `i2cdetect -y 1` to check address. It is probably `0x40`.

```python
from sensor import SHT20

# I2C bus=1, Address=0x40
sht = SHT20(1, 0x40)

h = sht.humidity()  # read humidity
print(h)            # namedtuple
print(h.RH)         # relative humidity

t = sht.temperature()  # read temperature
print(t)               # namedtuple
print(t.C)             # Celsius

h, t = sht.all()  # read both at once
```

## MCP3004

- Analog sensors (e.g. photoresistor) cannot interface with Raspberry Pi
  directly. They have to go through an A/D converter.

```python
from sensor import MCP3004

# SPI bus=0, CS=0, V_ref=3.3V
mcp = MCP3004(bus=0, addr=0, vref=3.3)

mcp.voltage(0)  # read voltage on channel 0
```
