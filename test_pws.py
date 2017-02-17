#WORKING
#!/usr/bin/python3
from sense_hat import SenseHat
import RPi.GPIO as GPIO
import time, math
import os
import time
from time import sleep
from datetime import datetime
import MySQLdb
import serial
import I2C_LCD_driver
import time
mylcd = I2C_LCD_driver.lcd()


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

#function for logging to excel file
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
    mylcd.lcd_display_string("CSV SUCCESS", 2) 

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
    
GPIO.setmode(GPIO.BCM)
GPIO.setup(wind_pin, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(rain_pin, GPIO.IN, GPIO.PUD_UP)
GPIO.add_event_detect(wind_pin, GPIO.FALLING, callback=spin)
GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=tip, bouncetime=300)
interval = 5

while True:
    mylcd.lcd_display_string("Time: %s" %time.strftime("%H:%M:%S"), 1)
    
    mylcd.lcd_display_string("Date: %s" %time.strftime("%m/%d/%Y"), 2)

    readingtime = datetime.now()
    wind_count = 0
    rain_count = 0
    time.sleep(interval)
    wspeed = calculate_speed(9.0, interval)
    rff = bucket_tipped(rf)
    sense_data=get_data()
    message = 'Temp in C* is {0} in F* is {1}  | Pressure is {2} mbars | Humidity is {3} percent | WindSpeed is {4} kph | Rainfall is {5} mm | \n'.format(sense_data[0],sense_data[1],sense_data[2],sense_data[3], wspeed, rff)
    print(message,'\n')
  
    try:
        #Open database connection
        db = MySQLdb.connect("169.254.138.89","root","raspi","readings")

        #prepare a cursor object using cursor method()
        cursor = db.cursor()
        
        sql= "INSERT INTO sensorreadings (time, tempC, tempF, press, humid, wspeed, rainfall) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (str(readingtime), str(sense_data[0]), str(sense_data[1]), str(sense_data[2]), str(sense_data[3]), str(wspeed), str(rff))

        try:
           #execute SQL QUERY USING EXECUTE METHOD()
            cursor.execute(sql)

            #commit changes in the database
            db.commit()
            mylcd.lcd_clear()
            mylcd.lcd_display_string("LOGGING SUCCESS", 1)

            try:
                csv_log()
            except:
                      mylcd.lcd_display_string("ERROR CSV ", 1)
        except:
            mylcd.lcd_display_string("ERROR LOGGING", 1)
            db.rollback()
            
    finally:
        #disconnect from server
        db.close()
        
    time.sleep(10)
    mylcd.lcd_clear()
        

#WORKING






     



