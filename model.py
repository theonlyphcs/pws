from peewee import *

mysql_db =MySQLDatabase('readings', user='root', passwd='raspi')


class sensorreadings(model):
    time = Charfield()
    tempC = Charfield()
    tempF = Charfield()
    press = Charfield()
    humid = Charfield()
    wspeed = Charfield()
    rainfall = Charfield()
    
    class Meta:
        database = mysql_db

class sensordata(object):
    "Main data access layer class which provides functions to query sensor reading data from database"

    def _init_(self):
        """initialise acces to the Sensor reading database"""
        #connect to Database.
        mysql_db.connect()
        #make sure the tables are created (safe=True, otherwise they might be deleted).
        mysql_db.create_tables([sensorreadings], safe=True)

    def get_recent_readings(self, limit=30):
        """return a list of the most recent reading the specified name, by default returns 30 readings, in descending order"""
        return sensorreadings.select() \
               .where(sensorreadings.name == name) \
               .order_by(sensorreadings.time.desc()) \
               .limit(limit)
    
    def add_reading(self, time, tempC, tempF, press, humid, wspeed, rainfall):
        """add the specified sensor reading to the database"""
        sensorreadings.create(time=time, tempC=tempC, tempF=tempF, press=press, humid=humid, wspeed=wspeed, rainfall=rainfall)

    def close(self):
        """close the connection to the database"""
        db.close()
