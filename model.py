from peewee import *

db = MySQLDatabase('thesis',host='169.254.84.210', port=3306, user='root', passwd='raspi')

class datareadings(Model):
    time = CharField()
    tempC = CharField()
    tempF = CharField()
    press = CharField()
    humid = CharField()
    wspeed = CharField()
    rainfall = CharField()
    
    class Meta:
        database = db

class dataObject(object):
    "Main data access layer class which provides functions to query sensor reading data from database"

    def _init_(self):
        """initialise acces to the Sensor reading database"""
        #connect to Database.
        db.connect()
        #make sure the tables are created (safe=True, otherwise they might be deleted).
        db.create_tables([datareadings], safe = True)

    def get_recent_readings(self, limit=30):
        """return a list of the most recent reading the specified name, by default returns 30 readings, in descending order"""
        return datareadings.select() \
               .where(datareadings.name == name) \
               .order_by(datareadings.time.desc()) \
               .limit(limit)
    
    def add_reading(self, time, tempC, tempF, press, humid, wspeed, rainfall):
        """add the specified sensor reading to the database"""
        datareadings.create(time=time, tempC=tempC, tempF=tempF, press=press, humid=humid, wspeed=wspeed, rainfall=rainfall)

    def close(self):
        """close the connection to the database"""
        db.close()
