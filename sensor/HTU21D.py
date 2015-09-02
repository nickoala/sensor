# Copyright 2014 IIJ Innovation Institute Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY IIJ INNOVATION INSTITUTE INC. ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL IIJ INNOVATION INSTITUTE INC. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Copyright 2014 Keiichi Shima. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import fcntl
import io
import struct
import time
import sensor

# fcntl
_I2C_SLAVE = 0x0703

# Default I2C address
_DEFAULT_ADDRESS = 0x40

# Configuration parameters
RESOLUTION_12BITS      = 0b00000000
RESOLUTION_8BITS       = 0b00000001
RESOLUTION_10BITS      = 0b10000000
RESOLUTION_11BITS      = 0b10000001
# _END_OF_BATTERY        = 0b01000000
# _ENABLE_ONCHIP_HEATER  = 0b00000100
_DISABLE_ONCHIP_HEATER = 0b00000000
_ENABLE_OTP_RELOAD     = 0b00000000
_DISABLE_OTP_RELOAD    = 0b00000010
_RESERVED_BITMASK      = 0b00111000

# Commands
_CMD_TEMPERATURE  = '\xF3'
_CMD_HUMIDITY     = '\xF5'
_CMD_WRITE_CONFIG = '\xE6'
_CMD_READ_CONFIG  = '\xE7'
_CMD_SOFT_RESET   = '\xFE'

# Data bits specification
_STATUS_BITMASK     = 0b00000011
_STATUS_TEMPERATURE = 0b00000000
_STATUS_HUMIDITY    = 0b00000010
_STATUS_LSBMASK     = 0b11111100

class HTU21D(sensor.SensorBase):
    def __init__(self, bus = None, addr = _DEFAULT_ADDRESS,
                 resolution = RESOLUTION_12BITS,
                 use_temperature = True):
        '''Initializes the sensor with some default values.
        bus: The SMBus descriptor on which this sensor is attached.
        addr: The I2C bus address
            (default is 0x40).
        '''
        assert(bus is not None)
        assert(addr > 0b0000111
               and addr < 0b1111000)
        assert(resolution == RESOLUTION_12BITS
               or resolution == RESOLUTION_8BITS
               or resolution == RESOLUTION_10BITS
               or resolution == RESOLUTION_11BITS)
        assert(use_temperature == True
               or use_temperature == False)

        super(HTU21D, self).__init__(self._update_sensor_data)

        self._ior = io.open('/dev/i2c-' + str(bus), 'rb', buffering=0)
        self._iow = io.open('/dev/i2c-' + str(bus), 'wb', buffering=0)
        fcntl.ioctl(self._ior, _I2C_SLAVE, addr)
        fcntl.ioctl(self._iow, _I2C_SLAVE, addr)

        self._resolution = resolution
        self._onchip_heater = _DISABLE_ONCHIP_HEATER
        self._otp_reload = _DISABLE_OTP_RELOAD

        self._humidity = None
        self._temperature = None
        self._use_temperature = use_temperature

        self._reset()
        self._reconfigure()

    @property
    def humidity(self):
        '''Returns a relative humidity value.  Returns None if no valid value
        is set yet.
        '''
        self._update()
        return (self._humidity)

    @property
    def temperature(self):
        '''Returns a temperature value.  Returns None if no valid value is set
        yet.
        '''
        if self._use_temperature is True:
            self._update()
        return (self._temperature)

    @property
    def use_temperature(self):
        '''Returns whether to measure temperature or not.
        '''
        return (self._use_temperature)

    @use_temperature.setter
    def use_temperature(self, use_temperature):
        assert(use_temperature == True
               or use_temperature == False)
        self._use_temperature = use_temperature

    @property
    def resolution(self):
        '''Gets/Sets the resolution of temperature value.
        RESOLUTION_12BITS: RH 12 bits, Temp 14 bits.
        RESOLUTION_8BITS:  RH  8 bits, Temp 12 bits.
        RESOLUTION_10BITS: RH 10 bits, Temp 13 bits.
        RESOLUTION_11BITS: RH 11 bits, Temp 11 bits.
        '''
        return (self._resolution)

    @resolution.setter
    def resolution(self, resolution):
        assert(resolution == RESOLUTION_12BITS
               or resolution == RESOLUTION_8BITS
               or resolution == RESOLUTION_10BITS
               or resolution == RESOLUTION_11BITS)
        self._resolution = resolution
        self._reconfigure()

    def _reset(self):
        self._iow.write(_CMD_SOFT_RESET)
        time.sleep(0.02)

    def _reconfigure(self):
        self._iow.write(_CMD_READ_CONFIG)
        configs = self._ior.read(1)
        (config,) = struct.unpack('B', configs)
        config = ((config & _RESERVED_BITMASK)
                  | self._resolution
                  | self._onchip_heater
                  | self._otp_reload)
        self._iow.write(_CMD_WRITE_CONFIG + struct.pack('B', config))

    def _update_sensor_data(self):
        if self._use_temperature is True:
            self._iow.write(_CMD_TEMPERATURE)
            time.sleep(0.05)
            vals = self._ior.read(3)
            (temphigh, templow, crc) = struct.unpack('BBB', vals)
            temp = (temphigh << 8) | (templow & _STATUS_LSBMASK)
            self._temperature = -46.85 + (175.72 * temp) / 2**16

        self._iow.write(_CMD_HUMIDITY)
        time.sleep(0.02)
        vals = self._ior.read(3)
        (humidhigh, humidlow, crc) = struct.unpack('BBB', vals)
        humid = (humidhigh << 8) | (humidlow & _STATUS_LSBMASK)
        self._humidity = -6 + (125.0 * humid) / 2**16

if __name__ == '__main__':

    bus = 1
    sensor = HTU21D(bus)
    for cache in [0, 5]:
        print '**********'
        print 'Cache lifetime is %d' % cache
        sensor.cache_lifetime = cache
        for c in range(10):
            for res in [RESOLUTION_12BITS,
                        RESOLUTION_8BITS,
                        RESOLUTION_10BITS,
                        RESOLUTION_11BITS]:
                sensor.resolution = res
                print sensor.humidity, sensor.temperature
