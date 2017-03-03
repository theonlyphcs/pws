#WORKING
#!/usr/bin/python3
from sense_hat import SenseHat
from i2clibraries import i2c_hmc5883l
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO
import time, math, os, serial, MySQLdb
import I2C_LCD_driver
mylcd = I2C_LCD_driver.lcd()

#connects to arduino
ser =serial.Serial('/dev/ttyUSB0',9600)

wind_pin = 21
rain_pin = 26
wind_count = 0
rain_count = 0
rf = 0

#for raingauge measurement
def bucket_tipped(rf):
    global rain_count
    rf=rain_count * 0.2794
    return rf

#for anemometer measurement
def calculate_speed(r_cm, time_sec):
    global wind_count
    circ_cm = (2 * math.pi) * r_cm
    rot = wind_count / 2.0
    dist_km = (circ_cm * rot) / 100000.0 # convert to kilometres
    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * 3600 # convert to distance per hour
    return km_per_hour * 1.18

#for anemometer measurement
def spin(channel):
    global wind_count
    wind_count += 1
   
#for raingauge measurement
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

#function for database logging
def log_data(): 
    mylcd.lcd_clear()
    try:
            #Open database connection
            db = MySQLdb.connect("192.168.254.101","root","raspi","readings")

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
        mylcd.lcd_display_string('Temp C*:' + str(sense_data[0]) +' deg', 1)
        mylcd.lcd_display_string('Temp F*:' + str(sense_data[1]) +' deg', 2)
        time.sleep(2)
        mylcd.lcd_clear()
        mylcd.lcd_display_string('Press:' + str(sense_data[2]) +' hPa', 1)
        mylcd.lcd_display_string('HUmid:' + str(sense_data[3]) +' %', 2)
        time.sleep(2)
        mylcd.lcd_clear()
        mylcd.lcd_display_string('WindS:' + str(wspeed) +' kph', 1)
        mylcd.lcd_display_string('RainF:' + str(rff) +' mm', 2)
        time.sleep(2)
        mylcd.lcd_display_string('WindD:' + str(wvane), 1)
        mylcd.lcd_display_string('PWS 2017 TUP MNL', 2)
        time.sleep(2)
        mylcd.lcd_clear()
        
def show_read():
    message = 'Temp in C* is {0} in F* is {1}  | Pressure is {2} mbars | Humidity is {3} percent | WindSpeed is {4:.2f} kph | Rainfall is {5} mm | WindDirection is {6} | '.format(sense_data[0],sense_data[1],sense_data[2],sense_data[3], wspeed, rff, wvane)
    print(message)
    ser.flush()
    message3 = 'TMP:{0}C,{1}F, PRES:{2}, HUM:{3}, WS:{4:.0f}kph, RF:{5:.1f}mm, WD:{6} '.format(sense_data[0],sense_data[1],sense_data[2],sense_data[3],wspeed,rff,wvane)
    ser.write(message3.encode())
    print("ok")
    ser.flush()
    

    
GPIO.setmode(GPIO.BCM)
GPIO.setup(wind_pin, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(rain_pin, GPIO.IN, GPIO.PUD_UP)
GPIO.add_event_detect(wind_pin, GPIO.FALLING, callback=spin)
GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=tip, bouncetime=300)
interval = 5

#MAIN LOOP
while True:
    mylcd.lcd_display_string("Time: %s" %time.strftime("%H:%M:%S"), 1) #shows time lcd 
    mylcd.lcd_display_string("Date: %s" %time.strftime("%m/%d/%Y"), 2) #shows date lcd
    #hmc5883l = i2c_hmc5883l.i2c_hmc5883l(1) # for windvane
    #hmc5883l.setContinuousMode() # for windvane
    #hmc5883l.setDeclination(0,6) # for windvane
    readingtime = datetime.now() #gets time
    wind_count = 0 #for anemometer
    rain_count = 0 #for raingauge, for anemometer
    time.sleep(interval) #for raingauge
    wspeed = calculate_speed(9.0, interval) #for anemometer
    rff = bucket_tipped(rf) #for raingauge
    sense_data=get_data() # gets temp, humidity, pressure data
    wvane =  "S.E"
    show_read()
    log_data()
    time.sleep(5)
	        
#WORKING
