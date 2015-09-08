# Raspberry Pi Sensors

This is a **Python** package that enables **Raspberry Pi** to read various sensors (and interact with some non-sensors). It has only been tested on **Python 2.7** running on **Raspbian** on Raspberry Pi **2** Model **B**.

Supported devices include:
- **DS18B20** temperature sensor
- **BMP180** pressure and temperature sensor
- **HTU21D** humidity and temperature sensor
- **ML8511** UV sensor
- **MCP3004** A/D Converter
- **LCD1602** display

The chief motivation for this package is educational. I am teaching a Raspberry Pi course, and find it very troublesome for students having to download a separate library every time they use another sensor. With this package, they download once and they are set (for my course, anyway). I hope you find the same level of convenience, if, for any reason, you decide to try out this package.

## Installation

It is best to update Linux first.

`sudo apt-get update`  
`sudo apt-get upgrade`

Then:

`sudo apt-get install python-pip` to install the Python package manager  
`sudo pip install sensor` to install this package

But the `sensor` package would not work by itself. Communicating with sensors often requires some sort of serial protocol, such as **1-wire**, **I2C**, or **SPI**. You have to know which sensor speaks which, and set up Linux and Python accordingly.

## Setup 1-Wire

`sudo nano /boot/config.txt`, add this line:
```
dtoverlay=w1-gpio
```
**Reboot.**

## Setup I2C

`sudo apt-get install i2c-tools python-smbus`

`sudo nano /etc/modules`, add this line:
```
i2c-dev
```

`sudo nano /boot/config.txt`, add this line:
```
dtparam=i2c1=on
```
**Reboot.**

## Setup SPI

`sudo apt-get install python-dev`  
`sudo pip install spidev`

`sudo nano /boot/config.txt`, add this line:
```
dtparam=spi=on
```
**Reboot.**

## Know your sensor's address

Unlike many libraries out there, this library knows **no default bus number** and **no default device address**. I want learners to be explicitly aware of those numbers, even if they are fixed.

*Numbers* that are useful to know:
- **I2C** bus is numbered **1**
- **SPI** bus is numbered **0**

To find out individual sensor's address:
- For 1-wire sensors, go to `/sys/bus/w1/devices/`, and look for a long sequence of numbers
- For I2C sensors, use `i2cdetect -y 1`
- For SPI sensors, you should know which CS pin you used

## More coming ...
