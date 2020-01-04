
Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-sht31d/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/sht31d/en/latest/
    :alt: Documentation Status

.. image :: https://img.shields.io/discord/327254708534116352.svg
    :target: https://discord.gg/nBQh6qu
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_SHT31D/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_SHT31D/actions/
    :alt: Build Status

CircuitPython module for the SHT31-D temperature and humidity sensor.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_


Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Installing from PyPI
====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-sht31d/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-sht31d

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-sht31d

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-sht31d
    
Usage Example
=============
You must import the library to use it:

.. code:: python

    import adafruit_sht31d

This driver takes an instantiated and active I2C object (from the `busio` or
the `bitbangio` library) as an argument to its constructor.  The way to create
an I2C object depends on the board you are using. For boards with labeled SCL
and SDA pins, you can:

.. code:: python

    from busio import I2C
    from board import SCL, SDA

    i2c = I2C(SCL, SDA)

Once you have created the I2C interface object, you can use it to instantiate
the sensor object:

.. code:: python

    sensor = adafruit_sht31d.SHT31D(i2c)


And then you can start measuring the temperature and humidity:

.. code:: python

    print(sensor.temperature)
    print(sensor.relative_humidity)

You can instruct the sensor to periodically measure the temperature and
humidity, storing the result in its internal cache:

.. code:: python

    sensor.mode = adafruit_sht31d.MODE_PERIODIC

You can adjust the frequency at which the sensor periodically gathers data to:
0.5, 1, 2, 4 or 10 Hz. The following adjusts the frequency to 2 Hz:

.. code:: python

    sensor.frequency = adafruit_sht31d.FREQUENCY_2

The sensor is capable of storing eight results. The sensor stores these
results in an internal FILO cache. Retrieving these results is simlilar to
taking a measurement. The sensor clears its cache once the stored data is read.
The sensor always returns eight data points. The list of results is backfilled
with the maximum output values of 130.0 ºC and 100.01831417975366 % RH:

.. code:: python

    print(sensor.temperature)
    print(sensor.relative_humidity)

The sensor will continue to collect data at the set interval until it is
returned to single shot data acquisition mode:

.. code:: python

    sensor.mode = adafruit_sht31d.MODE_SINGLE

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_SHT31D/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
