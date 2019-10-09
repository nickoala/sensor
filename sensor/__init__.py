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

import time
import threading

# Locks for buses: subclasses of SensorBase should apply the appropriate
# decorator(s) to ensure only one device is accessing a particular bus
# at any given moment.

_w1_lock = threading.Lock()

def w1_lock(func):
    def locked(*args, **kwargs):
        with _w1_lock:
            func(*args, **kwargs)
    return locked

_i2c_lock = threading.Lock()

def i2c_lock(func):
    def locked(*args, **kwargs):
        with _i2c_lock:
            func(*args, **kwargs)
    return locked

_spi_lock = threading.Lock()

def spi_lock(func):
    def locked(*args, **kwargs):
        with _spi_lock:
            func(*args, **kwargs)
    return locked

class SensorBase(object):
    def __init__(self, update_callback):
        assert (update_callback is not None)

        self._cache_lifetime = 0
        self._last_updated = None
        self._update_callback = update_callback

    def _update(self, **kwargs):
        now = time.time()

        # If caching is disabled, just update the data.
        if self._cache_lifetime > 0:
            # Check if the cached value is still valid or not.
            if (self._last_updated is not None
                and self._last_updated + self._cache_lifetime > now):
                # The value is still valid.
                return

        # Get the latest sensor values.
        try:
            self._update_callback(**kwargs)
            self._last_updated = now
        except:
            raise

        return

    @property
    def cache_lifetime(self):
        '''Gets/Sets the cache time (in seconds).
        '''
        return (self._cache_lifetime)

    @cache_lifetime.setter
    def cache_lifetime(self, cache_lifetime):
        assert(cache_lifetime >= 0)

        self._cache_lifetime = cache_lifetime


__all__ = ['DS18B20', 'SHT20', 'HTU21D', 'BMP180', 'MCP3004']

from .DS18B20 import DS18B20
from .SHT20 import SHT20
from .HTU21D import HTU21D
from .BMP180 import BMP180
from .MCP3004 import MCP3004
