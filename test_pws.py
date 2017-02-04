#EnviMainProgram
from i2clibraries import i2c_hmc5883l
from sense_hat import SenseHat
import time,math
import datetime
import csv
import RPi.GPIO as GPIO
import serial
import os
import spidev
    
#function for getting data
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

#function for logging to .csv format
def csv_log():
    

#start of main program
while True:
     sense_data=get_data()
     message = 'Temp in C* is {0} in F* is {1}  | Pressure is {2} mbars | Humidity is {3} percent | '.format(sense_data[0],sense_data[1],sense_data[2],sense_data[3])
     print(message)
     time.sleep(30)

     
     



