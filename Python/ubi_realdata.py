from multiprocessing import Process
import navio.util
import navio.ublox
import navio.ms5611
import time
import requests
import math
import random
import argparse
import sys
import numpy as np

TOKEN = "BBFF-Dpzfrql8SZQI69cGftAlnC09sLyiAf"  # Put your TOKEN here
DEVICE_LABEL = "RPi"  # Put your device label here 
VARIABLE_LABEL_1 = "Temperature"
VARIABLE_LABEL_2 = "Pressure"
VARIABLE_LABEL_3 = "Position"  
VARIABLE_LABEL_4 = "Speed"
VARIABLE_LABEL_5 = "Heading"
VARIABLE_LABEL_6 = "Acceleration"
VARIABLE_LABEL_7 = "Gyroscope"  
VARIABLE_LABEL_8 = "Magnetometer"
LATITUDE = 0
LONGITUDE = 0
TEMPERATURE = 0
PRESSURE = 0
GROUND_SPEED = 0
HEADING = 0
M9A = np.zeros(3)
M9G = np.zeros(3)
M9M = np.zeros(3)

def update_accel(accList, gyrList, magList):
    global M9A, M9G, M9M
    accList = [round(element,3) for element in accList]
    gyrList = [round(element,3) for element in gyrList]
    magList = [round(element,3) for element in magList]

    M9A = accList
    M9G = gyrList
    M9M = magList
    print(' '.join(str(x) for x in M9A))
    print(' '.join(str(x) for x in M9G))
    print(' '.join(str(x) for x in M9M))

def update_gps(GPSdict):
    global LATITUDE, LONGITUDE
    LATITUDE = int(GPSdict['Latitude'])/10000000.0
    LONGITUDE = int(GPSdict['Longitude'])/10000000.0

def update_baro(temperature, pressure):
    global TEMPERATURE, PRESSURE
    TEMPERATURE = temperature
    PRESSURE = pressure

def update_speed(speedDict):
    global GROUND_SPEED, HEADING
    GROUND_SPEED = int(speedDict['gSpeed'])
    HEADING = int(speedDict['heading'])/100000.0

def get_gps():
    return (LATITUDE, LONGITUDE)

def get_baro():
    return (TEMPERATURE, PRESSURE)

def get_speed():
    return (GROUND_SPEED, HEADING)

def get_accel():
    return (M9A, M9G, M9M)

def build_payload(variable_1, variable_2, variable_3, variable_4, variable_5, variable_6, variable_7, variable_8):
    lat, lng = get_gps()
    temp_value, pressure_value = get_baro()
    speed, heading = get_speed()
    m9a, m9g, m9m = get_accel()

    payload = {variable_1: temp_value,
               variable_2: pressure_value,
               variable_3: {"value": 1, "context": {"lat": lat, "lng": lng}},
               variable_4: speed,
               variable_5: heading,
               variable_6: {"value": 1, "context": {"x": m9a[0], "y": m9a[1], "z":m9a[2]}},
               variable_7: {"value": 1, "context": {"x": m9g[0], "y": m9g[1], "z":m9g[2]}},
               variable_8: {"value": 1, "context": {"x": m9m[0], "y": m9m[1], "z":m9m[2]}}
               }

    return payload

def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://things.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")

    return True

def main():
    time.sleep(1)

    payload = build_payload(
        VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3, VARIABLE_LABEL_4,
        VARIABLE_LABEL_5, VARIABLE_LABEL_6, VARIABLE_LABEL_7, VARIABLE_LABEL_8)

    print("[INFO] Attemping to send data")
    post_request(payload)
    print(payload)
    print("[INFO] finished")

def gpsThread():
    ubl = GPSConfig()
#    time.sleep(1)

    while(True):
        msg = ubl.receive_message()

        # print(msg.name())
        if msg is None:
            if opts.reopen:
                ubl.close()
                ubl = navio.ublox.UBlox("spi:0.0", baudrate=5000000, timeout=2)
                continue
            print(empty)

            break

        if msg.name() == "NAV_POSLLH":
            print("NAV_POSLLH")
            outstr = str(msg).split(",")[1:]
    #            print(outstr)
            names = list()
            values = list()
            for entry in outstr:
                new = entry.split('=')
                names.append(new[0][1:])
                values.append(new[1])
            GPSdict = dict(zip(names, values))
            print(GPSdict)
            update_gps(GPSdict)
            # print(outstr)
        if msg.name() == "NAV_STATUS":
            print("NAV_STATUS")
            outstr = str(msg).split(",")[1:2]
            outstr = "".join(outstr)
            print(outstr)
        if msg.name() == "NAV_VELNED":
            print("NAV_VELNED")
            print(str(msg))
            outstr = str(msg).split(",")[1:]
            names = list()
            values = list()
            for entry in outstr:
                new = entry.split('=')
                names.append(new[0][1:])
                values.append(new[1])
            speedDict = dict(zip(names, values))
            update_speed(speedDict)
            print(speedDict)

def accelThread(accelName):
    # AccelGyroMag initialization
    if accelName == 'mpu':
        print("Selected: MPU9250")
        imu = navio.mpu9250.MPU9250()
    else:
        print("Selected: LSM9DS1")
        imu = navio.lsm9ds1.LSM9DS1()
    
    if imu.testConnection():
        print('Connection to IMU established')
        imu.initialize()
    else:
        print('NO CONNECTION to IMU')

 #   time.sleep(1)
    while(True):        
        m9a, m9g, m9m = imu.getMotion9()
        update_accel(m9a, m9g, m9m)
    
def baroThread():
    # Barometer initialization
    baro = navio.ms5611.MS5611()
    baro.initialize()
    while(True):
        time.sleep(0.1)

        baro.refreshPressure()
        time.sleep(0.01) # Waiting for pressure data ready 10ms
        baro.readPressure()

        baro.refreshTemperature()
        time.sleep(0.01) # Waiting for temperature data ready 10ms
        baro.readTemperature()

        baro.calculatePressureAndTemperature()
        update_baro(baro.TEMP, baro.PRES)
        print('Temp: {:+7.3f} Baro:{:+7.3f}'.format(baro.TEMP, baro.PRES))

def GPSConfig():
    ubl = navio.ublox.UBlox("spi:0.0", baudrate=5000000, timeout=2)

    ubl.configure_poll_port()
    ubl.configure_poll(navio.ublox.CLASS_CFG, navio.ublox.MSG_CFG_USB)
    #ubl.configure_poll(navio.ublox.CLASS_MON, navio.ublox.MSG_MON_HW)

    ubl.configure_port(port=navio.ublox.PORT_SERIAL1, inMask=1, outMask=0)
    ubl.configure_port(port=navio.ublox.PORT_USB, inMask=1, outMask=1)
    ubl.configure_port(port=navio.ublox.PORT_SERIAL2, inMask=1, outMask=0)
    ubl.configure_poll_port()
    ubl.configure_poll_port(navio.ublox.PORT_SERIAL1)
    ubl.configure_poll_port(navio.ublox.PORT_SERIAL2)
    ubl.configure_poll_port(navio.ublox.PORT_USB)
    ubl.configure_solution_rate(rate_ms=1000)

    ubl.set_preferred_dynamic_model(None)
    ubl.set_preferred_usePPP(None)

    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_POSLLH, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_PVT, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_STATUS, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_SOL, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_VELNED, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_SVINFO, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_VELECEF, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_POSECEF, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_RXM, navio.ublox.MSG_RXM_RAW, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_RXM, navio.ublox.MSG_RXM_SFRB, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_RXM, navio.ublox.MSG_RXM_SVSI, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_RXM, navio.ublox.MSG_RXM_ALM, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_RXM, navio.ublox.MSG_RXM_EPH, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_TIMEGPS, 5)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_CLOCK, 5)
    #ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_DGPS, 5)

    return ubl

if __name__ == '__main__':
    navio.util.check_apm()

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help = "Sensor selection: -i [sensor name].\
                                    Sensors names: mpu or lsm.")
    
    if (len(sys.argv) == 1):
        print("Using LSM9DS1 as default accelerometer")
        parser.print_help()
    elif len(sys.argv) == 2:
        print("Enter sensor name: mpu or lsm")

    args = parser.parse_args()

    aThread = Process(target=accelThread, args=(args.i, ))
        
    gThread = Process(target=gpsThread)
    bThread = Process(target=baroThread)
        # mainThread = Process(target=main())
    
    bThread.start()
    gThread.start()
    aThread.start()
    aThread.join()
    bThread.join()
    gThread.join()

    main()      

        

