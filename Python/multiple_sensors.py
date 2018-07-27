import time
import navio.ms5611
import navio.util
import sys
import navio.leds


navio.util.check_apm()

baro = navio.ms5611.MS5611()
led = navio.leds.Led()
led.setColor('Green')
print("LED is Green")

baro.initialize()

time.sleep(1)
count = 0
while(True):
    if (count%2==0):
        led.setColor('Yellow')
        print("LED is Yellow")
    elif (count%2==1):
        led.setColor('Green')
        print("LED is Green")
    else:
        led.setColor('Red')

    baro.refreshPressure()
    time.sleep(0.01)
    baro.readPressure()

    baro.refreshTemperature()
    time.sleep(0.01)
    baro.readTemperature()
    baro.calculatePressureAndTemperature()
    print("Temperature(C): %0.6f" %(baro.TEMP), "Pressure(millibar): %.6f" %(baro.PRES))
    time.sleep(1)


    count+=1
