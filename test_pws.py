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
import time
import serial
from i2clibraries import i2c_hmc5883l
import I2C_LCD_driver
import time
mylcd = I2C_LCD_driver.lcd()

ser =serial.Serial('/dev/ttyUSB0',9600)


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
            file.write("Time,TempCelsius,TempFarenheit,Pressure,Humidity,Windspeed,Rainfall,WindDirection\n")
    i=i+1
    now = datetime.now()
    file.write(str(now)+","+ str(sense_data[0]) +","+ str(sense_data[1]) +","+ str(sense_data[2]) +","+ str(sense_data[3])+","+ str(wspeed) +","+ str(rff) +","+ str(wvane) +"\n")
    file.flush()
    file.close()
    print("CSV SUCCESS"+'\n')

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

def log_data():
    try:
            #Open database connection
            db = MySQLdb.connect("169.254.138.89","root","raspi","readings")

            #prepare a cursor object using cursor method()
            cursor = db.cursor()
                
            sql= "INSERT INTO sensorreadings (time, tempC, tempF, press, humid, wspeed, rainfall, wdirection) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (str(readingtime), str(sense_data[0]), str(sense_data[1]), str(sense_data[2]), str(sense_data[3]), str(wspeed), str(rff), str(wvane))

            try:
                #execute SQL QUERY USING EXECUTE METHOD()
                cursor.execute(sql)

                #commit changes in the database
                db.commit()
                print("LOGGING SUCCESS")

                try:
                    csv_log()
                    #ser.flush()
                except:
                    #mylcd.lcd_display_string("ERROR CSV ", 1)
                    print("ERROR CSV")
            except:
                #mylcd.lcd_display_string("ERROR LOGGING", 1)
                print("ERROR DB")
                db.rollback()
                    
    finally:
        #disconnect from server
        db.close()
        
        lcd1 = 'Temp C*:'+ str(sense_data[0])
        ser.write(lcd1.encode())
        time.sleep(1)
        ser.flush()

        lcd2 ='Temp F*:' +str(sense_data[1])
        ser.write(lcd2.encode())
        time.sleep(1)
        ser.flush()
        
        lcd3 = 'Humidity:'+str(sense_data[3])+'%'
        ser.write(lcd3.encode())
        time.sleep(1)
        ser.flush()
        
        lcd4 = 'RainF:'+ str(rff) +'mm'
        ser.write(lcd4.encode())
        time.sleep(1)
        ser.flush()

        lcd5 = 'Pressure:'+ str(sense_data[2]) +'hpa'
        ser.write(lcd5.encode())
        time.sleep(1)
        ser.flush()
        
        lcd6 = 'WindS:'+str(wspeed) +'kph'
        ser.write(lcd6.encode())
        time.sleep(1)
        ser.flush()
        
        lcd7 = 'WindD:' + str(wvane)
        ser.write(lcd7.encode())
        time.sleep(1)
        ser.flush()

        lcd8 = 'PWS 2017'
        ser.write(lcd8.encode())
        time.sleep(1)
        ser.flush()
        
def show_read():
    message = 'Temp in C* is {0} in F* is {1}  | Pressure is {2} mbars | Humidity is {3} percent | WindSpeed is {4} kph | Rainfall is {5} mm | WindDirection is {6} | '.format(sense_data[0],sense_data[1],sense_data[2],sense_data[3], wspeed, rff, wvane)
    print(message)
    

    
GPIO.setmode(GPIO.BCM)
GPIO.setup(wind_pin, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(rain_pin, GPIO.IN, GPIO.PUD_UP)
GPIO.add_event_detect(wind_pin, GPIO.FALLING, callback=spin)
GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=tip, bouncetime=300)
interval = 5

#MAIN LOOP
while True:
    mylcd.lcd_display_string("Time: %s" %time.strftime("%H:%M:%S"), 1)
    
    mylcd.lcd_display_string("Date: %s" %time.strftime("%m/%d/%Y"), 2)
    hmc5883l = i2c_hmc5883l.i2c_hmc5883l(1)
    hmc5883l.setContinuousMode()
    hmc5883l.setDeclination(0,6)
    readingtime = datetime.now()
    wind_count = 0
    rain_count = 0
    time.sleep(interval)
    wspeed = calculate_speed(9.0, interval)
    rff = bucket_tipped(rf)
    sense_data=get_data()
    wd = str(hmc5883l)
    #print(wd)
    wd2 = int(wd)
    if wd2 == 0 or wd2 == 360:
        #print("North")
        wvane ="North"
        show_read()
        log_data()
        
    elif wd2 > 0 and wd2 < 90:
        #print("North East")
        wvane ="North East"
        show_read()
        log_data()
        
    elif wd2 == 90:
        #print ("East")
        wvane = "East"
        show_read()
        log_data()
        
    elif wd2 == 180:
        #print("South")
        wvane = "South"
        show_read()
        log_data()

        
    elif wd2 >90 and wd2 < 180:
        #print("South East")
        wvane = "South East"
        show_read()
        log_data()

    elif wd2 > 180 and wd2 < 270:
        #print("South West")
        wvane = "South West"
        show_read()
        log_data()
        
    elif wd2 >270 and wd2 < 360:
        #print("North West")
        wvane = "North West"
        show_read()
        log_data()
        
    elif wd2 == 270:
        #print("West")
        wvane = "West"
        show_read()
        log_data()
        
    else:
        log_data()
        
#WORKING
