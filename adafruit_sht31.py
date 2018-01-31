# The MIT License (MIT)
#
# Copyright (c) 2017 Jerry Needell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_sht31`
====================================================

This is a CircuitPython driver for the SHT31-D temperature and humidity sensor.

"""

# imports
try:
    import struct
except ImportError:
    import ustruct as struct

import time

from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_sht31.git"


SHT31_DEFAULT_ADDR = const(0x44)
SHT31_MEAS_HIGHREP_STRETCH = const(0x2C06)
SHT31_MEAS_MEDREP_STRETCH = const(0x2C0D)
SHT31_MEAS_LOWREP_STRETCH = const(0x2C10)
SHT31_MEAS_HIGHREP = const(0x2400)
SHT31_MEAS_MEDREP = const(0x240B)
SHT31_MEAS_LOWREP = const(0x2416)
SHT31_READSTATUS = const(0xF32D)
SHT31_CLEARSTATUS = const(0x3041)
SHT31_SOFTRESET = const(0x30A2)
SHT31_HEATEREN = const(0x306D)
SHT31_HEATERDIS = const(0x3066)


def _crc(data):
    crc = 0xff
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc <<= 1
                crc ^= 0x131
            else:
                crc <<= 1
    return crc


class SHT31:
    """
    A driver for the SHT31-D temperature and humidity sensor.
    """
    def __init__(self, i2c_bus, address=SHT31_DEFAULT_ADDR):
        self.i2c_device = I2CDevice(i2c_bus, address)
        self._command(SHT31_SOFTRESET)
        time.sleep(.010)

    def _command(self, command):
        with self.i2c_device as i2c:
            i2c.write(struct.pack('>H', command))

    def _data(self):
        data = bytearray(6)
        data[0] = 0xff
        self._command(SHT31_MEAS_HIGHREP)
        time.sleep(.5)
        with self.i2c_device as i2c:
            i2c.readinto(data)
        temperature, tcheck, humidity, hcheck = struct.unpack('>HBHB', data)
        if tcheck != _crc(data[:2]):
            raise RuntimeError("temperature CRC mismatch")
        if hcheck != _crc(data[3:5]):
            raise RuntimeError("humidity CRC mismatch")
        return temperature, humidity

    @property
    def temperature(self):
        """The measured relative humidity in percent."""
        raw_temperature, _ = self._data()
        return -45 + (175 * (raw_temperature / 65535))

    @property
    def relative_humidity(self):
        """The measured relative humidity in percent."""
        _, raw_humidity = self._data()
        return 100 * (raw_humidity / 65523)

    def reset(self):
        """Execute a Soft RESET of the sensor."""
        self._command(SHT31_SOFTRESET)
        time.sleep(.010)

    @property
    def heater(self):
        """Control the sensor internal heater."""
        return (self.status & 0x2000) != 0

    @heater.setter
    def heater(self, value=False):
        if value:
            self._command(SHT31_HEATEREN)
        else:
            self._command(SHT31_HEATERDIS)

    @property
    def status(self):
        """Return the Sensor status."""
        data = bytearray(2)
        self._command(SHT31_READSTATUS)
        with self.i2c_device as i2c:
            i2c.readinto(data)
        status = data[0] << 8 | data[1]
        return status
