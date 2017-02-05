#WORKING
#!/usr/bin/python3

import RPi.GPIO as GPIO
import time, math
import os
import time 
from time import sleep
from datetime import datetime

wind_pin = 21
rain_pin = 26
wind_count = 0
rain_count = 0
rf = 0

def bucket_tipped(rf):
    global rain_count
    rf=rain_count * 0.2794
    return rf

def calculate_speed(r_cm, time_sec):
    global wind_count
    circ_cm = (2 * math.pi) * r_cm
    rot = wind_count / 2.0
    dist_km = (circ_cm * rot) / 100000.0 # convert to kilometres
    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * 3600 # convert to distance per hour
    return km_per_hour * 1.18

def spin(channel):
    global wind_count
    wind_count += 1
   

def tip(channel2):
    global rain_count
    rain_count += 1

def log():
    file = open("/media/pi/SONDISK/data_log.csv", "a")
    i=0
    if os.stat("/media/pi/SONDISK/data_log.csv").st_size == 0:
            file.write("Time,TempCelsius,TempFarenheit,Pressure,Humidity,Windspeed,Rainfall\n")
    i=i+1
    now = datetime.now()
    file.write(str(now)+","+ str(tempC) +","+ str(tempF) +","+ str(press) +","+ str(humid)+","+ str(wspeed) +","+ str(rff) +"\n")
    file.flush()
    file.close()

GPIO.setmode(GPIO.BCM)
GPIO.setup(wind_pin, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(rain_pin, GPIO.IN, GPIO.PUD_UP)
GPIO.add_event_detect(wind_pin, GPIO.FALLING, callback=spin)
GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=tip, bouncetime=300)
interval = 5

while True:
    wind_count = 0
    rain_count = 0
    time.sleep(interval)
    wspeed = calculate_speed(9.0, interval)
    rff = bucket_tipped(rf)
    print ("Windspeed: ",wspeed, "kph" ,wind_count)
    print ("Rainfall: ",rff, "mm", rain_count)
    time.sleep(interval)
    

#WORKING





