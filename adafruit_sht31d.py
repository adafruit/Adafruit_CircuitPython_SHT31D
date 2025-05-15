# SPDX-FileCopyrightText: 2017 Jerry Needell for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Llewelyn Trahaearn for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_sht31d`
====================================================

This is a CircuitPython driver for the SHT31-D temperature and humidity sensor.

* Author(s): Jerry Needell, Llewelyn Trahaearn

Implementation Notes
--------------------

**Hardware:**

* Adafruit SHT31-D temperature and humidity sensor Breakout: https://www.adafruit.com/product/2857

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

# imports
import struct
import time

from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

try:
    from typing import List, Tuple, Union

    from busio import I2C
    from circuitpython_typing import ReadableBuffer
    from typing_extensions import Literal
except ImportError:
    pass


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_SHT31D.git"


_SHT31_DEFAULT_ADDRESS = const(0x44)
_SHT31_SECONDARY_ADDRESS = const(0x45)

_SHT31_ADDRESSES = (_SHT31_DEFAULT_ADDRESS, _SHT31_SECONDARY_ADDRESS)

_SHT31_READSERIALNBR = const(0x3780)
_SHT31_READSTATUS = const(0xF32D)
_SHT31_CLEARSTATUS = const(0x3041)
_SHT31_HEATER_ENABLE = const(0x306D)
_SHT31_HEATER_DISABLE = const(0x3066)
_SHT31_SOFTRESET = const(0x30A2)
_SHT31_NOSLEEP = const(0x303E)
_SHT31_PERIODIC_FETCH = const(0xE000)
_SHT31_PERIODIC_BREAK = const(0x3093)

MODE_SINGLE = "Single"
MODE_PERIODIC = "Periodic"

_SHT31_MODES = (MODE_SINGLE, MODE_PERIODIC)

REP_HIGH = "High"
REP_MED = "Medium"
REP_LOW = "Low"

_SHT31_REP = (REP_HIGH, REP_MED, REP_LOW)

FREQUENCY_0_5 = 0.5
FREQUENCY_1 = 1
FREQUENCY_2 = 2
FREQUENCY_4 = 4
FREQUENCY_10 = 10

_SHT31_FREQUENCIES = (
    FREQUENCY_0_5,
    FREQUENCY_1,
    FREQUENCY_2,
    FREQUENCY_4,
    FREQUENCY_10,
)

_SINGLE_COMMANDS = (
    (REP_LOW, const(False), const(0x2416)),
    (REP_MED, const(False), const(0x240B)),
    (REP_HIGH, const(False), const(0x2400)),
    (REP_LOW, const(True), const(0x2C10)),
    (REP_MED, const(True), const(0x2C0D)),
    (REP_HIGH, const(True), const(0x2C06)),
)

_PERIODIC_COMMANDS = (
    (True, None, const(0x2B32)),
    (REP_LOW, FREQUENCY_0_5, const(0x202F)),
    (REP_MED, FREQUENCY_0_5, const(0x2024)),
    (REP_HIGH, FREQUENCY_0_5, const(0x2032)),
    (REP_LOW, FREQUENCY_1, const(0x212D)),
    (REP_MED, FREQUENCY_1, const(0x2126)),
    (REP_HIGH, FREQUENCY_1, const(0x2130)),
    (REP_LOW, FREQUENCY_2, const(0x222B)),
    (REP_MED, FREQUENCY_2, const(0x2220)),
    (REP_HIGH, FREQUENCY_2, const(0x2236)),
    (REP_LOW, FREQUENCY_4, const(0x2329)),
    (REP_MED, FREQUENCY_4, const(0x2322)),
    (REP_HIGH, FREQUENCY_4, const(0x2334)),
    (REP_LOW, FREQUENCY_10, const(0x272A)),
    (REP_MED, FREQUENCY_10, const(0x2721)),
    (REP_HIGH, FREQUENCY_10, const(0x2737)),
)

_DELAY = ((REP_LOW, 0.0045), (REP_MED, 0.0065), (REP_HIGH, 0.0155))


def _crc(data) -> int:
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc <<= 1
                crc ^= 0x31
            else:
                crc <<= 1
    return crc & 0xFF


def _unpack(data: ReadableBuffer) -> List[int]:
    length = len(data)
    crc = [None] * (length // 3)
    word = [None] * (length // 3)
    for i in range(length // 6):
        word[i * 2], crc[i * 2], word[(i * 2) + 1], crc[(i * 2) + 1] = struct.unpack(
            ">HBHB", data[i * 6 : (i * 6) + 6]
        )
        if crc[i * 2] == _crc(data[i * 6 : (i * 6) + 2]):
            length = (i + 1) * 6
    for i in range(length // 3):
        if crc[i] != _crc(data[i * 3 : (i * 3) + 2]):
            raise RuntimeError("CRC mismatch")
    return word[: length // 3]


class SHT31D:
    """
    A driver for the SHT31-D temperature and humidity sensor.

    :param ~busio.I2C i2c_bus: The I2C bus the SHT31-D is connected to
    :param int address: (optional) The I2C address of the device. Defaults to :const:`0x44`

    **Quickstart: Importing and using the SHT31-D**

        Here is an example of using the :class:`SHT31D` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            import board
            import adafruit_sht31d

        Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()   # uses board.SCL and board.SDA
            sht = adafruit_sht31d.SHT31D(i2c)

        Now you have access to the temperature and humidity the
        the :attr:`temperature` and :attr:`relative_humidity` attributes


        .. code-block:: python

            temperature = sht.temperature
            humidity = sht.relative_humidity

    """

    def __init__(self, i2c_bus: I2C, address: int = _SHT31_DEFAULT_ADDRESS) -> None:
        if address not in _SHT31_ADDRESSES:
            raise ValueError(f"Invalid address: {hex(address)}")
        self.i2c_device = I2CDevice(i2c_bus, address)
        self._mode = MODE_SINGLE
        self._repeatability = REP_HIGH
        self._frequency = FREQUENCY_4
        self._clock_stretching = False
        self._art = False
        self._last_read = 0
        self._cached_temperature = None
        self._cached_humidity = None
        self._reset()

    def _command(self, command: int) -> None:
        with self.i2c_device as i2c:
            i2c.write(struct.pack(">H", command))

    def _reset(self) -> None:
        """
        Soft reset the device
        The reset command is preceded by a break command as the
        device will not respond to a soft reset when in 'Periodic' mode.
        """
        self._command(_SHT31_PERIODIC_BREAK)
        time.sleep(0.001)
        self._command(_SHT31_SOFTRESET)
        time.sleep(0.0015)

    def _periodic(self) -> None:
        for command in _PERIODIC_COMMANDS:
            if self.art == command[0] or (
                self.repeatability == command[0] and self.frequency == command[1]
            ):
                self._command(command[2])
                time.sleep(0.001)
                self._last_read = 0

    def _data(self) -> Union[Tuple[float, float], Tuple[List[float], List[float]]]:
        if self.mode == MODE_PERIODIC:
            data = bytearray(48)
            data[0] = 0xFF
            self._command(_SHT31_PERIODIC_FETCH)
            time.sleep(0.001)
        elif self.mode == MODE_SINGLE:
            data = bytearray(6)
            data[0] = 0xFF
            for command in _SINGLE_COMMANDS:
                if self.repeatability == command[0] and self.clock_stretching == command[1]:
                    self._command(command[2])
            if not self.clock_stretching:
                for delay in _DELAY:
                    if self.repeatability == delay[0]:
                        time.sleep(delay[1])
            else:
                time.sleep(0.001)
        with self.i2c_device as i2c:
            i2c.readinto(data)
        word = _unpack(data)
        length = len(word)
        temperature = [None] * (length // 2)
        humidity = [None] * (length // 2)
        for i in range(length // 2):
            temperature[i] = -45 + (175 * (word[i * 2] / 65535))
            humidity[i] = 100 * (word[(i * 2) + 1] / 65535)
        if (len(temperature) == 1) and (len(humidity) == 1):
            return temperature[0], humidity[0]
        return temperature, humidity

    def _read(self) -> Union[Tuple[float, float], Tuple[List[float], List[float]]]:
        if self.mode == MODE_PERIODIC and time.time() > self._last_read + 1 / self.frequency:
            self._cached_temperature, self._cached_humidity = self._data()
            self._last_read = time.time()
        elif self.mode == MODE_SINGLE:
            self._cached_temperature, self._cached_humidity = self._data()
        return self._cached_temperature, self._cached_humidity

    @property
    def mode(self) -> Literal["Single", "Periodic"]:
        """
        Operation mode
        Allowed values are the constants MODE_*
        Return the device to 'Single' mode to stop periodic data acquisition and allow it to sleep.
        """
        return self._mode

    @mode.setter
    def mode(self, value: Literal["Single", "Periodic"]) -> None:
        if not value in _SHT31_MODES:
            raise ValueError(f"Mode '{value}' not supported")
        if self._mode == MODE_PERIODIC and value != MODE_PERIODIC:
            self._command(_SHT31_PERIODIC_BREAK)
            time.sleep(0.001)
        if value == MODE_PERIODIC and self._mode != MODE_PERIODIC:
            self._periodic()
        self._mode = value

    @property
    def repeatability(self) -> Literal["High", "Medium", "Low"]:
        """
        Repeatability
        Allowed values are the constants REP_*
        """
        return self._repeatability

    @repeatability.setter
    def repeatability(self, value: Literal["High", "Medium", "Low"]) -> None:
        if not value in _SHT31_REP:
            raise ValueError("Repeatability '{value}' not supported")
        if self.mode == MODE_PERIODIC and not self._repeatability == value:
            self._repeatability = value
            self._periodic()
        else:
            self._repeatability = value

    @property
    def clock_stretching(self) -> bool:
        """
        Control clock stretching.
        This feature only affects 'Single' mode.
        """
        return self._clock_stretching

    @clock_stretching.setter
    def clock_stretching(self, value: bool) -> None:
        self._clock_stretching = bool(value)

    @property
    def art(self) -> bool:
        """
        Control accelerated response time
        This feature only affects 'Periodic' mode.
        """
        return self._art

    @art.setter
    def art(self, value: bool) -> None:
        if value:
            self.frequency = FREQUENCY_4
        if self.mode == MODE_PERIODIC and not self._art == value:
            self._art = bool(value)
            self._periodic()
        else:
            self._art = bool(value)

    @property
    def frequency(self) -> float:
        """
        Periodic data acquisition frequency
        Allowed values are the constants FREQUENCY_*
        Frequency can not be modified when ART is enabled
        """
        return self._frequency

    @frequency.setter
    def frequency(self, value: float) -> None:
        if self.art:
            raise RuntimeError("Frequency locked to '4 Hz' when ART enabled")
        if not value in _SHT31_FREQUENCIES:
            raise ValueError("Data acquisition frequency '{value} Hz' not supported")
        if self.mode == MODE_PERIODIC and not self._frequency == value:
            self._frequency = value
            self._periodic()
        else:
            self._frequency = value

    @property
    def temperature(self) -> Union[float, List[float]]:
        """
        The measured temperature in degrees Celsius.
        'Single' mode reads and returns the current temperature as a float.
        'Periodic' mode returns the most recent readings available from the sensor's cache
        in a FILO list of eight floats. This list is backfilled with with the
        sensor's maximum output of 130.0 when the sensor is read before the
        cache is full.
        """
        temperature, _ = self._read()
        return temperature

    @property
    def relative_humidity(self) -> Union[float, List[float]]:
        """
        The measured relative humidity in percent.
        'Single' mode reads and returns the current humidity as a float.
        'Periodic' mode returns the most recent readings available from the sensor's cache
        in a FILO list of eight floats. This list is backfilled with with the
        sensor's maximum output of 100.01831417975366 when the sensor is read
        before the cache is full.
        """
        _, humidity = self._read()
        return humidity

    @property
    def heater(self) -> bool:
        """Control device's internal heater."""
        return (self.status & 0x2000) != 0

    @heater.setter
    def heater(self, value: bool = False) -> None:
        if value:
            self._command(_SHT31_HEATER_ENABLE)
            time.sleep(0.001)
        else:
            self._command(_SHT31_HEATER_DISABLE)
            time.sleep(0.001)

    @property
    def status(self) -> int:
        """Device status."""
        data = bytearray(2)
        self._command(_SHT31_READSTATUS)
        time.sleep(0.001)
        with self.i2c_device as i2c:
            i2c.readinto(data)
        status = data[0] << 8 | data[1]
        return status

    @property
    def serial_number(self) -> int:
        """Device serial number."""
        data = bytearray(6)
        data[0] = 0xFF
        self._command(_SHT31_READSERIALNBR)
        time.sleep(0.001)
        with self.i2c_device as i2c:
            i2c.readinto(data)
        word = _unpack(data)
        return (word[0] << 16) | word[1]
