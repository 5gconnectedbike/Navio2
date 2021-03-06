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
import queue
import navio.leds

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
    LATITUDE = 0
    LONGITUDE = 0
    TEMPERATURE = 0
    PRESSURE = 0
    GROUND_SPEED = 0
    HEADING = 0
    M9A = np.zeros(3)
    M9G = np.zeros(3)
    M9M = np.zeros(3)
    
    def __init__(self):
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

        aThread = Process(target=self.accelThread, args=(args.i, aQueue, ))
            
        gThread = Process(target=self.gpsThread, args=(gQueue, sQueue, ))
        bThread = Process(target=self.baroThread, args=(bQueue,))
        mainThread = Process(target=self.main, args=(bQueue, aQueue, gQueue, sQueue))
        
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
        # self.LATITUDE = 0
        # self.LONGITUDE = 0
        # self.TEMPERATURE = 0
        # self.PRESSURE = 0
        # self.GROUND_SPEED = 0
        # self.HEADING = 0
        # self.M9A = np.zeros(3)
        # self.M9G = np.zeros(3)
        # self.M9M = np.zeros(3)

    @classmethod
    def update_accel(cls, accList, gyrList, magList):
        # global M9A, M9G, M9M
        accList = [round(element,3) for element in accList]
        gyrList = [round(element,3) for element in gyrList]
        magList = [round(element,3) for element in magList]

        cls.M9A = accList
        cls.M9G = gyrList
        cls.M9M = magList
        print('Accel: {:+7.3f} {:+7.3f} {:+7.3f}'.format(cls.M9M[0],cls.M9M[1],cls.M9M[2]))

#        print(' '.join(str(x) for x in M9A))
#        print(' '.join(str(x) for x in M9G))
        # print(' '.join(str(x) for x in cls.M9M))

    @classmethod
    def update_gps(cls, GPSdict):
        # global LATITUDE, LONGITUDE
        cls.LATITUDE = int(GPSdict['Latitude'])/10000000.0
        cls.LONGITUDE = int(GPSdict['Longitude'])/10000000.0

    @classmethod
    def update_baro(cls, temperature, pressure):
        # global TEMPERATURE, PRESSURE
        cls.TEMPERATURE = temperature
        cls.PRESSURE = pressure
        print('UPDATE:  TEMP: {} PRESSURE: {}'.format(cls.TEMPERATURE, cls.PRESSURE))

    @classmethod
    def update_speed(cls, speedDict):
        # global GROUND_SPEED, HEADING
        cls.GROUND_SPEED = int(speedDict['gSpeed'])
        cls.HEADING = int(speedDict['heading'])/100000.0

    @classmethod
    def get_gps(cls):
        # print('')
        return (cls.LATITUDE, cls.LONGITUDE)

    @classmethod
    def get_baro(cls):
        print('GET: TEMP: {} PRESSURE: {}'.format(cls.TEMPERATURE, cls.PRESSURE))
        return (cls.TEMPERATURE, cls.PRESSURE)

    @classmethod
    def get_speed(cls):
        return (cls.GROUND_SPEED, cls.HEADING)

    @classmethod
    def get_accel(cls):
        return (cls.M9A, cls.M9G, cls.M9M)

    def build_payload(self, variable_1, variable_2, variable_3, variable_4, variable_5, variable_6, variable_7, variable_8, bQ, aQ, gQ, sQ):
        # lat, lng = Ubidots.get_gps()
        temp_value, pressure_value = bQ.get()
        speedDict = sQ.get()
        gpsDict = gQ.get()
        m9a, m9g, m9m = aQ.get()

        m9a = [round(element,3) for element in m9a]
        m9g = [round(element,3) for element in m9g]
        m9m = [round(element,3) for element in m9m]
        
        speed = int(speedDict['gSpeed'])
        heading = int(speedDict['heading'])/100000.0

        lat = int(gpsDict['Latitude'])/10000000.0
        lng = int(gpsDict['Longitude'])/10000000.0


        # temp_value, pressure_value = Ubidots.get_baro()
        # speed, heading = Ubidots.get_speed()
        # m9a, m9g, m9m = Ubidots.get_accel()
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

    def main(self, bQ, aQ, gQ, sQ):
        while True:
            led = navio.leds.Led()
            led.setColor('Yellow')
            # time.sleep(3)

            payload = self.build_payload(
                Ubidots.VARIABLE_LABEL_1, Ubidots.VARIABLE_LABEL_2, Ubidots.VARIABLE_LABEL_3, Ubidots.VARIABLE_LABEL_4,
                Ubidots.VARIABLE_LABEL_5, Ubidots.VARIABLE_LABEL_6, Ubidots.VARIABLE_LABEL_7, Ubidots.VARIABLE_LABEL_8, bQ, aQ, gQ, sQ)

            print("[INFO] Attemping to send data")
            self.post_request(payload)
            print(payload)
            print("[INFO] finished")
            led.setColor('Green')

    def gpsThread(self, gQ, sQ):
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
                gQ.put(GPSdict)
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
                sQ.put(speedDict)
                # print(speedDict)

    def accelThread(self, accelName, aQ):
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
            aQ.put((m9a, m9g, m9m))
            time.sleep(5)
    
    @classmethod
    def baroThread(cls, bQ):
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
            bQ.put((baro.TEMP, baro.PRES))
            cls.update_baro(baro.TEMP, baro.PRES)
            # print('Temp: {:+7.3f} Baro:{:+7.3f}'.format(baro.TEMP, baro.PRES))
            time.sleep(5)

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
            

