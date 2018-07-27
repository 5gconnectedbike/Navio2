import time
import requests
import math
import random

TOKEN = "BBFF-Dpzfrql8SZQI69cGftAlnC09sLyiAf"  # Put your TOKEN here
DEVICE_LABEL = "RPi"  # Put your device label here 
VARIABLE_LABEL_1 = "temperature"  # Put your first variable label here
VARIABLE_LABEL_2 = "humidity"  # Put your second variable label here
VARIABLE_LABEL_3 = "position"  # Put your second variable label here
VARIABLE_LABEL_4 = "pressure"
VARIABLE_LABEL_5 = "voltage"
VARIABLE_LABEL_6 = "accelerometer"
VARIABLE_LABEL_7 = "gyroscope"
VARIABLE_LABEL_8 = "magnetometer"


def build_payload(variable_1, variable_2, variable_3, variable_4, variable_5, variable_6, variable_7, variable_8):
    # Creates two random values for sending data
    value_1 = random.randint(-10, 50)
    value_2 = random.randint(0, 85)
    

    # Creates a random gps coordinates
    lat = random.randrange(34, 36, 1) + \
        random.randrange(1, 1000, 1) / 1000.0
    lng = random.randrange(-83, -87, -1) + \
        random.randrange(1, 1000, 1) / 1000.0
    payload = {variable_1: temp_value,
               variable_2: humidity_value,
               variable_3: {"value": 1, "context": {"lat": lat, "lng": lng}},
               variable_4: pressure_value,
               variable_5: {"context":{"A0": a0, "A1": a1, "A2": a2, "A3": a3, "A4": a4, "A5": a5}},
               variable_6: {"context":{"x": acc_x, "y": acc_y, "z": acc_z}},
               variable_7: {"context":{"x": gyro_x, "y": gyro_y, "z": gyro_z}},
               variable_8: {"context":{"x": mag_x, "y": mag_y, "z": mag_z}},
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
    while (True):
        main()
        time.sleep(1)