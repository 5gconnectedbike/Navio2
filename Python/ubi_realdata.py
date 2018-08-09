from multiprocessing import Process, Queue
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

class Ubidots:
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
    # LATITUDE = 0
    # LONGITUDE = 0
    # TEMPERATURE = 0
    # PRESSURE = 0
    # GROUND_SPEED = 0
    # HEADING = 0
    # M9A = np.zeros(3)
    # M9G = np.zeros(3)
    # M9M = np.zeros(3)
    
    def __init__(self):
        
        self.LATITUDE = 0
        self.LONGITUDE = 0
        self.TEMPERATURE = 0
        self.PRESSURE = 0
        self.GROUND_SPEED = 0
        self.HEADING = 0
        self.M9A = np.zeros(3)
        self.M9G = np.zeros(3)
        self.M9M = np.zeros(3)

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

        aQueue = Queue()
        bQueue = Queue()
        gQueue = Queue()
        sQueue = Queue()

        aThread = Process(target=self.accelThread, args=(args.i, ))
            
        gThread = Process(target=self.gpsThread)
        bThread = Process(target=self.baroThread)
        mainThread = Process(target=self.main)
        
        bThread.start()
        gThread.start()
        aThread.start()
        mainThread.start()

        aThread.join()
        bThread.join()
        gThread.join()
        mainThread.join()

        # self.TOKEN = "BBFF-Dpzfrql8SZQI69cGftAlnC09sLyiAf"  # Put your TOKEN here
        # self.DEVICE_LABEL = "RPi"  # Put your device label here 
        # self.VARIABLE_LABEL_1 = "Temperature"
        # self.VARIABLE_LABEL_2 = "Pressure"
        # self.VARIABLE_LABEL_3 = "Position"  
        # self.VARIABLE_LABEL_4 = "Speed"
        # self.VARIABLE_LABEL_5 = "Heading"
        # self.VARIABLE_LABEL_6 = "Acceleration"
        # self.VARIABLE_LABEL_7 = "Gyroscope"  
        # self.VARIABLE_LABEL_8 = "Magnetometer"


    def update_accel(self, accList, gyrList, magList):
        # global M9A, M9G, M9M
        accList = [round(element,3) for element in accList]
        gyrList = [round(element,3) for element in gyrList]
        magList = [round(element,3) for element in magList]

        self.M9A = accList
        self.M9G = gyrList
        self.M9M = magList
        print('Accel: {:+7.3f} {:+7.3f} {:+7.3f}'.format(self.M9M[0],self.M9M[1],self.M9M[2]))

    def update_gps(self, GPSdict):
        # global LATITUDE, LONGITUDE
        self.LATITUDE = int(GPSdict['Latitude'])/10000000.0
        self.LONGITUDE = int(GPSdict['Longitude'])/10000000.0

    def update_baro(self, temperature, pressure):
        # global TEMPERATURE, PRESSURE
        self.TEMPERATURE = temperature
        self.PRESSURE = pressure
        print('TEMP: {} PRESSURE: {}'.format(self.TEMPERATURE, self.PRESSURE))

    def update_speed(self, speedDict):
        # global GROUND_SPEED, HEADING
        self.GROUND_SPEED = int(speedDict['gSpeed'])
        self.HEADING = int(speedDict['heading'])/100000.0

    def get_gps(self):
        # print('')
        return (self.LATITUDE, self.LONGITUDE)

    def get_baro(self):
        return (self.TEMPERATURE, self.PRESSURE)

    def get_speed(self):
        return (self.GROUND_SPEED, self.HEADING)

    def get_accel(self):
        return (self.M9A, self.M9G, self.M9M)

    def build_payload(self, variable_1, variable_2, variable_3, variable_4, variable_5, variable_6, variable_7, variable_8):
        lat, lng = self.get_gps()
        temp_value = self.TEMPERATURE
        pressure_value = self.PRESSURE
        
        speed, heading = self.get_speed()
        m9a, m9g, m9m = self.get_accel()
        # print('lat: {} lng: {} temp_value: {} pressure value: {} m9m:{} {} {}'.format(lat, lng, temp_value, pressure_value, m9m[0], m9m[1], m9m[2]))

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

    def post_request(self, payload):
        # Creates the headers for the HTTP requests
        url = "http://things.ubidots.com"
        url = "{}/api/v1.6/devices/{}".format(url, self.DEVICE_LABEL)
        headers = {"X-Auth-Token": self.TOKEN, "Content-Type": "application/json"}

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

    def main(self):
        while True:
            time.sleep(3)

            payload = self.build_payload(
                Ubidots.VARIABLE_LABEL_1, Ubidots.VARIABLE_LABEL_2, Ubidots.VARIABLE_LABEL_3, Ubidots.VARIABLE_LABEL_4,
                Ubidots.VARIABLE_LABEL_5, Ubidots.VARIABLE_LABEL_6, Ubidots.VARIABLE_LABEL_7, Ubidots.VARIABLE_LABEL_8)

            print("[INFO] Attemping to send data")
            self.post_request(payload)
            print(payload)
            print("[INFO] finished")

    def gpsThread(self):
        ubl = self.GPSConfig()
    #    time.sleep(1)

        while(True):
            msg = ubl.receive_message()

            # print(msg.name())
            if msg is None:
                if opts.reopen:
                    ubl.close()
                    ubl = navio.ublox.UBlox("spi:0.0", baudrate=5000000, timeout=2)
                    continue
                # print(empty)

                break

            if msg.name() == "NAV_POSLLH":
                # print("NAV_POSLLH")
                outstr = str(msg).split(",")[1:]
        #            print(outstr)
                names = list()
                values = list()
                for entry in outstr:
                    new = entry.split('=')
                    names.append(new[0][1:])
                    values.append(new[1])
                GPSdict = dict(zip(names, values))
                # print(GPSdict)
                self.update_gps(GPSdict)
                # gQ = dequeue(values)

                # print(outstr)
            if msg.name() == "NAV_STATUS":
                # print("NAV_STATUS")
                outstr = str(msg).split(",")[1:2]
                outstr = "".join(outstr)
                # print(outstr)
            if msg.name() == "NAV_VELNED":
                # print("NAV_VELNED")
                # print(str(msg))
                outstr = str(msg).split(",")[1:]
                names = list()
                values = list()
                for entry in outstr:
                    new = entry.split('=')
                    names.append(new[0][1:])
                    values.append(new[1])
                speedDict = dict(zip(names, values))
                self.update_speed(speedDict)
                # print(speedDict)

    def accelThread(self, accelName):
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
            self.update_accel(m9a, m9g, m9m)
            time.sleep(1)
        
    def baroThread(self):
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
            self.update_baro(baro.TEMP, baro.PRES)
            # print('Temp: {:+7.3f} Baro:{:+7.3f}'.format(baro.TEMP, baro.PRES))
            time.sleep(1)

    def GPSConfig(self):
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

if __name__ =='__main__':
    ubidots = Ubidots()
            

