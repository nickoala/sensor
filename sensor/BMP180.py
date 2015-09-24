# Copyright 2015 Nick Lee
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

# Include the sensor directory, so this file may be run as a test script.
if __name__ == "__main__" and __package__ is None:
    import os, sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import struct
import time
import smbus
import sensor
from sensor.util import Pressure, Temperature

# Registers
_REG_AC1                 = 0xAA
_REG_AC2                 = 0xAC
_REG_AC3                 = 0xAE
_REG_AC4                 = 0xB0
_REG_AC5                 = 0xB2
_REG_AC6                 = 0xB4
_REG_B1                  = 0xB6
_REG_B2                  = 0xB8
_REG_MB                  = 0xBA
_REG_MC                  = 0xBC
_REG_MD                  = 0xBE
_REG_CALIB_OFFSET        = _REG_AC1
_REG_CONTROL_MEASUREMENT = 0xF4
_REG_DATA                = 0xF6

# Commands
_CMD_START_CONVERSION    = 0b00100000
_CMD_TEMPERATURE         = 0b00001110
_CMD_PRESSURE            = 0b00010100

# Oversampling mode
OS_MODE_SINGLE = 0b00
OS_MODE_2      = 0b01
OS_MODE_4      = 0b10
OS_MODE_8      = 0b11

# Conversion time (in second)
_WAIT_TEMPERATURE = 0.0045
_WAIT_PRESSURE    = [0.0045, 0.0075, 0.0135, 0.0255]

class BMP180(sensor.SensorBase):
    def __init__(self, bus, addr, os_mode = OS_MODE_SINGLE):
        assert(addr > 0b000111 and addr < 0b1111000)

        super(BMP180, self).__init__(
            update_callback = self._update_sensor_data)

        self._bus = smbus.SMBus(bus)
        self._addr = addr

        self._ac0 = None
        self._ac1 = None
        self._ac2 = None
        self._ac3 = None
        self._ac4 = None
        self._ac5 = None
        self._ac6 = None
        self._b1 = None
        self._b2 = None
        self._mb = None
        self._mc = None
        self._md = None
        self._os_mode = os_mode
        self._pressure = None
        self._temperature = None

        self._read_calibration_data()

    def pressure(self):
        '''Returns a pressure value.  Returns None if no valid value is set
        yet.
        '''
        self._update()
        return Pressure(hPa=self._pressure)

    def temperature(self):
        '''Returns a temperature value.  Returns None if no valid value is
        set yet.
        '''
        self._update()
        return Temperature(C=self._temperature)

    def all(self):
        '''Returns pressure and temperature values as a tuple.  This call can
        save 1 transaction than getting a pressure and temperature
        values separetely.  Returns (None, None) if no valid values
        are set yet.
        '''
        self._update()
        return (Pressure(hPa=self._pressure), Temperature(C=self._temperature))

    @property
    def os_mode(self):
        '''Gets/Sets oversampling mode.
        OS_MODE_SINGLE: Single mode.
        OS_MODE_2: 2 times.
        OS_MODE_4: 4 times.
        OS_MODE_8: 8 times.
        '''
        return (self._os_mode)

    @os_mode.setter
    def os_mode(self, os_mode):
        assert(os_mode == OS_MODE_SINGLE
               or os_mode == OS_MODE_2
               or os_mode == OS_MODE_4
               or os_mode == OS_MODE_8)
        self._os_mode = os_mode

    def _read_calibration_data(self):
        calib = self._bus.read_i2c_block_data(self._addr,
                                              _REG_CALIB_OFFSET, 22)
        (self._ac1, self._ac2, self._ac3, self._ac4,
         self._ac5, self._ac6, self._b1, self._b2,
         self._mb, self._mc, self._md) = struct.unpack(
             '>hhhHHHhhhhh', ''.join([chr(x) for x in calib]))

    @sensor.i2c_lock
    def _update_sensor_data(self):
        cmd = _CMD_START_CONVERSION | _CMD_TEMPERATURE
        self._bus.write_byte_data(self._addr,
                                  _REG_CONTROL_MEASUREMENT, cmd)
        time.sleep(_WAIT_TEMPERATURE)
        vals = self._bus.read_i2c_block_data(self._addr,
                                             _REG_DATA, 2)
        ut = vals[0] << 8 | vals[1]

        cmd = _CMD_START_CONVERSION | self._os_mode << 6 | _CMD_PRESSURE
        self._bus.write_byte_data(self._addr,
                                  _REG_CONTROL_MEASUREMENT, cmd)
        time.sleep(_WAIT_PRESSURE[self._os_mode])
        vals = self._bus.read_i2c_block_data(self._addr,
                                             _REG_DATA, 3)
        up = (vals[0] << 16 | vals[1] << 8 | vals[0]) >> (8 - self._os_mode)

        x1 = ((ut - self._ac6) * self._ac5) >> 15
        x2 = (self._mc << 11) / (x1 + self._md)
        b5 = x1 + x2
        self._temperature = ((b5 + 8) / 2**4) / 10.0

        b6 = b5 - 4000
        x1 = self._b2 * ((b6 * b6) >> 12)
        x2 = self._ac2 * b6
        x3 = (x1 + x2) >> 11
        b3 = (((self._ac1 *4 + x3) << self._os_mode) + 2) >> 2
        x1 = (self._ac3 * b6) >> 13
        x2 = (self._b1 * (b6 * b6) >> 12) >> 16
        x3 = ((x1 + x2) + 2) >> 2
        b4 = (self._ac4 * (x3 + 32768)) >> 15
        b7 = (up - b3) * (50000 >> self._os_mode)
        if (b7 < 0x80000000):
            p = (b7 * 2) / b4
        else:
            p = (b7 / b4) * 2
        x1 = p**2 >> 16
        x1 = (x1 * 3038) >> 16
        x2 = (-7357 * p) >> 16
        self._pressure = (p + ((x1 + x2 + 3791) >> 4)) / 100.0


""" Run this file as a test script
$ i2cdetect -y 1  # find the sensor's I2C address
$ python BMP180.py <bus> <hex address>

On Raspi, it is probably:
$ python BMP180.py 1 0x77
"""
if __name__ == '__main__':
    import sys

    bus = int(sys.argv[1])
    addr = int(sys.argv[2], 16)

    sensor = BMP180(bus, addr)
    for cache in [0, 5]:
        print '**********'
        print 'Cache lifetime is %d' % cache
        sensor.cache_lifetime = cache
        for mode in [OS_MODE_SINGLE, OS_MODE_2, OS_MODE_4, OS_MODE_8]:
            sensor.os_mode = mode
            print 'Oversampling mode is %d' % mode
            for c in range(10):
                print sensor.all()
