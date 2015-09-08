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

import sensor
from sensor.util import UV

class ML8511(sensor.SensorBase):
    def __init__(self, adc, channel):
        super(ML8511, self).__init__(self._update_sensor_data)

        self._adc = adc
        self._channel = channel
        self._mW_cm2 = None  # UV intensity: mW/cm2

    def uv(self):
        self._update()
        return UV(mW_cm2=self._mW_cm2)

    def _update_sensor_data(self):
        voltage = self._adc.voltage(self._channel)
        self._mW_cm2 = (voltage - 1) * 25 / 3.0


""" Run this file as a test script
$ python ML8511.py <spi_bus> <spi_chip_select> <channel> <v_ref>

On Raspi, if you put the ADC (MCP300X) on CS0, and connect 
the ML8511's output to ADC's input channel 0, with a ref voltage of 3.3V,
the command is:

$ python ML8511.py 0 0 0 3.3
"""
if __name__ == '__main__':
    import sys, time
    from sensor import MCP3004

    bus, cs, channel = map(int, sys.argv[1:4])
    vref = float(sys.argv[4])

    mcp = MCP3004.MCP3004(bus, cs, vref)
    ml = ML8511(mcp, channel)
    
    for i in range(0, 30):
        print ml.uv()
        time.sleep(1)
