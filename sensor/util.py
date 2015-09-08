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

from collections import namedtuple

class UV(namedtuple('UV', ['mW_cm2'])):
    pass

class Temperature(namedtuple('Temperature', ['C', 'F', 'K'])):
    def __new__(cls, **kwargs):
        if len(kwargs) != 1:
            raise RuntimeError('Specify temperature in one and only one unit: C, F, K')

        if 'C' in kwargs:
            kwargs['F'] = kwargs['C'] * 1.8 + 32
            kwargs['K'] = kwargs['C'] + 273.15
        elif 'F' in kwargs:
            kwargs['C'] = (kwargs['F'] - 32) / 1.8
            kwargs['K'] = kwargs['C'] + 273.15
        elif 'K' in kwargs:
            kwargs['C'] = kwargs['K'] - 273.15
            kwargs['F'] = kwargs['C'] * 1.8 + 32
        else:
            raise RuntimeError('Specify temperature in either: C, F, K')

        return super(Temperature, cls).__new__(cls, **kwargs)

class Humidity(namedtuple('Humidity', ['RH'])):
    pass

class Altitude(namedtuple('Altitude', ['m', 'ft'])):
    def __new__(cls, **kwargs):
        if len(kwargs) != 1:
            raise RuntimeError('Specify altitude in one and only one unit: m, ft')

        if 'm' in kwargs:
            kwargs['ft'] = kwargs['m'] * 3.28083998
        elif 'ft' in kwargs:
            kwargs['m'] = kwargs['ft'] * 0.3048
        else:
            raise RuntimeError('Specify altitude in either: m, ft')

        return super(Altitude, cls).__new__(cls, **kwargs)

class Pressure(namedtuple('Pressure', ['hPa'])):
    def altitude(self, msl):
        msl = msl.hPa if type(msl) is Pressure else msl
        m = 44330 * (1 - (self.hPa / msl)**(1 / 5.255))
        return Altitude(m=m)

    def msl_pressure(self, altitude):
        m = altitude.m if type(altitude) is Altitude else altitude
        hPa = self.hPa / (1.0 - m/44330.0)**5.255
        return Pressure(hPa=hPa)
