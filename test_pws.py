#MainProgram

from sense_hat import SenseHat
from time import sleep
from datetime import datetime
import csv
import time,math
import RPi.GPIO as GPIO
import serial
import os
import spidev

wspeed=0
rff=0
wind_pin = 21
rain_pin = 26
wind_count = 0
rain_count = 0
interval =5

##### function for getting data from senseHAT #####
def get_data():     
     sense_data =[]  
     sense = SenseHat()
     tempC = round(sense.get_temperature())
     sense_data.append(tempC)
     tempF = round(sense.get_temperature_from_pressure()*1.8 +32)
     sense_data.append(tempF)
     press = round(sense.get_pressure())
     sense_data.append(press)
     humid = round(sense.get_humidity())
     sense_data.append(humid)
     return sense_data

##### function for rainfall computation
def bucket_tipped(rf):
    global rain_count
    rf=rain_count * 0.2794 #0.2794 Milimeters per bucket
    return rf

##### function for windspeed computation
def calculate_speed(r_cm, time_sec):
    global wind_count
    circ_cm = (2 * math.pi) * r_cm
    rot = wind_count / 2.0
    dist_km = (circ_cm * rot) / 100000.0 # convert to kilometres
    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * 3600 # convert to distance per hour
    return km_per_hour * 1.18

##### additional function for windspeed computation 
def spin(channel):
    global wind_count
    wind_count += 1

##### additional function for windspeed computation 
def tip(channel2):
    global rain_count
    rain_count += 1

###### function for logging to excel file
def csv_log():
    file = open("/media/pi/SONDISK/data_log.csv", "a")
    i=0
    if os.stat("/media/pi/SONDISK/data_log.csv").st_size == 0:
            file.write("Time,TempCelsius,TempFarenheit,Pressure,Humidity,Windspeed,Rainfall\n")
    i=i+1
    now = datetime.now()
    file.write(str(now)+","+ str(sense_data[0]) +","+ str(sense_data[1]) +","+ str(sense_data[2]) +","+ str(sense_data[3])+","+ str(wspeed) +","+ str(rff) +"\n")
    file.flush()
    file.close()
    print("...success logging \n")

###### start of main program #####
while True:
     sense_data=get_data()
     message = 'Temp in C* is {0} in F* is {1}  | Pressure is {2} mbars | Humidity is {3} percent | \n'.format(sense_data[0],sense_data[1],sense_data[2],sense_data[3])
     csv_log()
     print ("Windspeed: ",calculate_speed(9.0, interval), "kph" ,wind_count)
     print ("Rainfall: ",bucket_tipped(rf), "mm", rain_count)
     print(message)
     time.sleep(30)

     
     



