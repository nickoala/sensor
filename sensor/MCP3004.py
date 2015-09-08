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

import spidev
import sensor

class MCP3004(object):
    def __init__(self, bus, addr, vref):
        super(MCP3004, self).__init__()

        self._vref = vref
        self._spi = spidev.SpiDev()
        self._spi.open(bus, addr)

    def read(self, channel):
        r = self._spi.xfer2([1, (8+channel) << 4, 0])
        out = ((r[1]&3) << 8) + r[2]
        return out

    def voltage(self, channel):
        return self._vref * self.read(channel) / 1024.0
