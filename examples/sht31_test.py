import time
import board
import busio
import adafruit_sht31

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31.SHT31(i2c)


while True:
    print(sensor.get_temperature_humidity)
    print(sensor.get_temperature)
    print(sensor.get_humidity)
    print(sensor.get_status)
    print(sensor.get_heater_status)
    print(sensor.set_heater(heater=True))
    print(sensor.get_heater_status)
    print(sensor.get_status)
    print(sensor.set_heater(heater=False))
    print(sensor.get_status)
    print(sensor.set_heater(heater=True))
    print(sensor.get_heater_status)
    print(sensor.get_status)
    sensor.reset
    print(sensor.get_status)
    print(sensor.get_heater_status)
    print(sensor.get_temperature_humidity)
    time.sleep(2)
