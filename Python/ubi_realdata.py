import navio.util
import navio.ublox
import navio.ms5611
import time
import requests
import math
import random

TOKEN = "BBFF-Dpzfrql8SZQI69cGftAlnC09sLyiAf"  # Put your TOKEN here
DEVICE_LABEL = "RPi"  # Put your device label here 
VARIABLE_LABEL_1 = "Temperature"
VARIABLE_LABEL_2 = "Pressure"
VARIABLE_LABEL_3 = "Position"  # Put your second variable label here
LATITUDE = 0
LONGITUDE = 0
TEMPERATURE = 0
PRESSURE = 0

def update_gps(GPSdict):
    global LATITUDE, LONGITUDE
    LATITUDE = int(GPSdict['Latitude'])
    LONGITUDE = int(GPSdict['Longitude'])

def update_baro(temperature, pressure):
    global TEMPERATURE, PRESSURE
    TEMPERATURE = temperature
    PRESSURE = pressure

def update_speed(speedDict):
    print('speed')
    print(speedDict)

def get_gps():
    return (LATITUDE, LONGITUDE, TEMPERATURE, PRESSURE)

def build_payload(variable_1, variable_2, variable_3):
    lat, lng, temp_value, pressure_value = get_gps()
    lat/= 10000000.0
    lng/= 10000000.0

    payload = {variable_1: temp_value,
               variable_2: pressure_value,
               variable_3: {"value": 1, "context": {"lat": lat, "lng": lng}}
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
    payload = build_payload(
        VARIABLE_LABEL_1, VARIABLE_LABEL_2, VARIABLE_LABEL_3)

    print("[INFO] Attemping to send data")
    post_request(payload)
    print(payload)
    print("[INFO] finished")


if __name__ == '__main__':

    navio.util.check_apm()

    baro = navio.ms5611.MS5611()
    baro.initialize()

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

    while (True):
        baro.refreshPressure()
        time.sleep(0.01) # Waiting for pressure data ready 10ms
        baro.readPressure()

        baro.refreshTemperature()
        time.sleep(0.01) # Waiting for temperature data ready 10ms
        baro.readTemperature()

        baro.calculatePressureAndTemperature()
        update_baro(baro.TEMP, baro.PRES)


        msg = ubl.receive_message()

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
            main()
            time.sleep(1)
            # outstr = "".join(outstr)
            # print(outstr)
        if msg.name() == "NAV_STATUS":
            print("NAV_STATUS")
            outstr = str(msg).split(",")[1:2]
            outstr = "".join(outstr)
            print(outstr)
        if msg.name() == "NAV_VELNED":
            print("NAV_VELNED")
            print(str(msg))
            outstr = str(msg).split(" ")[1:]
            outstr = "".join(outstr)
            names = list()
            values = list()
            for entry in outstr:
                new = entry.split('=')
                names.append(new[0])
                values.append(new[1])
            speedDict = dict(zip(names, values))
            update_speed(speedDict)
            # print(speedDict)

        

