import time
import board
import busio
import adafruit_sht31

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31.SHT31(i2c)


while True:
    print(sensor.temperature_and_relative_humidity)
    print(sensor.temperature)
    print(sensor.relative_humidity)
    print(sensor.status)
    print(sensor.heater_status)
    print(sensor.heater(heater=True))
    print(sensor.heater_status)
    print(sensor.status)
    print(sensor.heater(heater=False))
    print(sensor.status)
    print(sensor.heater(heater=True))
    print(sensor.heater_status)
    print(sensor.status)
    sensor.reset
    print(sensor.status)
    print(sensor.heater_status)
    print(sensor.temperature_and_relative_humidity)
    time.sleep(2)
