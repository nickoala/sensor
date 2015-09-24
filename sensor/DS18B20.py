# The MIT License (MIT)
# 
# Copyright (c) 2015 Nick Lee
# 
# Permission is hereby granted, free of charge, to any person obtaining 
# a copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

# Include the sensor directory, so this file may be run as a test script.
if __name__ == "__main__" and __package__ is None:
    import os, sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
import sensor
from sensor.util import Temperature

class DS18B20(sensor.SensorBase):
    def __init__(self, addr):
        super(DS18B20, self).__init__(self._update_sensor_data)

        self._device = '/sys/bus/w1/devices/%s/w1_slave' % addr
        self._temperature = None

    def temperature(self):
        self._update()
        return Temperature(C=self._temperature) if self._temperature is not None else None

    @sensor.w1_lock
    def _update_sensor_data(self):
        # Try at most 3 times
        for i in range(0,3):
            # Split output into separate lines.
            lines = subprocess.check_output(['cat', self._device]).split('\n')

            # If the first line does not end with 'YES', try again.
            if lines[0][-3:] != 'YES':
                time.sleep(0.2)
                continue

            # If the second line does not have a 't=', try again.
            pos = lines[1].find('t=')
            if pos < 0:
                time.sleep(0.2)
                continue

            # Extract the temperature.
            self._temperature = float(lines[1][pos+2:]) / 1000.0
            return

        # Failed reading
        self._temperature = None


""" Run this file as a test script
1. Find the sensor's 1-wire address

$ cd /sys/bus/w1/devices
$ ls

Look for '28-..........'. That is the address.

Then:
$ python DS18B20.py <address>
"""
if __name__ == '__main__':
    import sys, time

    ds = DS18B20(sys.argv[1])
    
    for i in range(0, 30):
        print ds.temperature()
        time.sleep(1)
