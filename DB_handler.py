import sqlite3 as sql
import datetime as datetime
import time as time
import utils
import math
import io
from shutil import copyfile
import os


class Database_handler():

    def __init__(self):
        self.con = None
        self.connectionState = False

        self.VERSION = 1.0

    def open_database(self, doInit):
        '''

        :param pathToDB:
        :param doInit: if database needs to be initialized
        :return: Error codes:   1 -> okay
                                -1 -> opening failed
                                -2 -> version may not be supported
        '''

        pathToDB = "/home/pi/jHomeHumidity/databases/HomeHumidity.db"

        if doInit:
            # database to setup -> copy Template
            if os.path.exists("/home/pi/jHomeHumidity/databases/jTemplate.db"):
                if not os.path.exists("/home/pi/jHomeHumidity/databases/HomeHumidty.db"):
                    copyfile("/home/pi/jHomeHumidity/databases/jTemplate.db",
                             "/home/pi/jHomeHumidity/databases/HomeHumidity.db")
                    print("Database initialized...")
            else:
                print("Error: Template database not found!")
                return -1

        try:
            self.con = sql.connect(pathToDB)
            self.connectionState = True

            print("Database_handler: opened database successfully")

            # try to get version of database
            dbVersion = float(self.getKeyValue(**{"key": "gen_version"}))
            if dbVersion != self.VERSION:
                # raise error for wrong version
                return -2
            return 1

        except Exception as eer:
            print("Database_handler: opened database failed")
            print(eer.__str__())
            return -1

    def close(self):
        if self.connectionState:
            self.con.commit()
            self.con.close()

        self.connectionState = False

    '''*****************************'''
    '''*** Public add methods ******'''
    '''*****************************'''

    def addupdatekeyValue(self, keyname, value):

        keyCurs = self.con.cursor()

        try:
            # check if keyname is already used
            valueCheck = self.getKeyValue(**{"key": keyname})

            if len(valueCheck) == 0:
                # key-value pair is not existing
                keyCurs.execute('INSERT into KeyValues VALUES (NULL,?,?)', (keyname, value))
                self.con.commit()
            else:
                # key-value pair is existing
                keyCurs.execute('UPDATE KeyValues set Value = ? WHERE Key = ?', (value, keyname))
                self.con.commit()
                print("Update on key " + str(keyname) + ":  " + str(value))

        except Exception as e:
            self.con.rollback()
            print("(addupdatekeyValue): error when writing data in database " + e.__str__())

    def addSensorMeasurement(self, meteoMeas):

        '''
        Function to insert measurement into database

        :param meteoMeas: (dict) containing fields (temp, press, humi)
        :return: boolean -> if it worked
        '''
        # check if input contains necessary fields
        if meteoMeas.get("temp", False) and meteoMeas.get("press", False) and meteoMeas.get("humi", False) :
            timeStamp = datetime.datetime.now().strftime("Y-M-d H:i:s")

            meteoCurs = self.con.cursor()

            meteoCurs.execute("Insert into MeteoData Values (NULL,?, ?, ?, ?)",
                              (timeStamp, meteoMeas.get("temp"), meteoMeas.get("press"), meteoMeas.get("humi"),))

            self.con.commit()
            return True
        else:
            return False

    def addAction(self, action):

        '''
        Function to add any action done by the controller into the database
        :param action: (dict) containing fields (timeStamp, actionType, comment)
        :return: boolean -> if it worked
        '''

        # check if input contains necessary fields
        if action.get("timeStamp", False) and action.get("actionType", False) and action.get("comment", False):
            actionCurs = self.con.cursor()

            actionCurs.execute("Insert into ActionData Values (NULL,?, ?, ?)",
                              (action.get("timeStamp"), action.get("actionType"), action.get("comment", ""),))

            self.con.commit()
            return True
        else:
            return False


    '''**************************'''
    '''*** Public get-methods ***'''
    '''**************************'''

    def getKeyValue(self, **kwargs):

        keycurs = self.con.cursor()

        if "keygroup" in kwargs:
            # key group requested
            keycurs.execute("SELECT * FROM KeyValues WHERE Key LIKE \'" + kwargs["keygroup"] + "%\'")

            data = keycurs.fetchall()
            dataDict = {}

            for entr in data:
                dataDict[entr[1]] = entr[2]

            return dataDict

        elif "key" in kwargs:
            keycurs.execute("SELECT Value FROM KeyValues WHERE Key = ?", (kwargs["key"],))

            data = keycurs.fetchone()

            if data is not None:
                return data[0]
            else:
                return ""

    def getMeteoMeasurements(self, minTimeStamp, maxTimeStamp):

        '''
        Function to return measured meteo data from the database
        :param minTimeStamp: (unix time) start timestamp of measured data returned; if None -> not limited
        :param maxTimeStamp: (unix time) end timestamp of measured data returned; if None -> not limited
        :return: (array) of desired data
        '''

        meteoCurs = self.con.cursor()

        requestString = "SELECT * from MeteoData "

        if minTimeStamp is not None:

            requestString += "WHERE Epoch > " + minTimeStamp + " "
            if maxTimeStamp is not None:

                requestString += "AND Epoch <  " + maxTimeStamp + " "

        if minTimeStamp is None and maxTimeStamp is not None:

            requestString += " WHERE Epoch < " + maxTimeStamp + " "

        print("Request from getMeteoMeasurements: " + requestString)

        meteoCurs.execute(requestString)

        data = meteoCurs.fetchall()

        if data is not None:
            dataPackage = []
            for row in data:
                dataPackage.append({"epoch": row[1], "temp": float(row[2]), "press": float(row[3]), "humi": float(row[4])})

            return dataPackage
        else:
            return None

    def getActions(self, minTimeStamp, maxTimeStamp, actionType):

        '''
        Function to get the executed actions
        :param minTimeStamp: (timeStamp) of start date for data request
        :param maxTimeStamp:  (timeStamp) of end of date for data request
        :param actionType: (string)
        :return: (array) of desired data
        '''

        actCurs = self.con.cursor()

        requestString = "SELECT * from ActionData "

        if minTimeStamp is not None:

            requestString += "WHERE Epoch > " + minTimeStamp + " "
            if maxTimeStamp is not None:
                requestString += "AND Epoch <  " + maxTimeStamp + " "

        if minTimeStamp is None and maxTimeStamp is not None:
            requestString += " WHERE Epoch < " + maxTimeStamp + " "

        if actionType is not None:
            if minTimeStamp is not None or maxTimeStamp is not None:

                requestString += " AND ActionType = " + actionType + " "
            else:

                requestString += "WHERE actionType = " + actionType + " "

        print("Request from getActions: " + requestString)

        actCurs.execute(requestString)

        data = actCurs.fetchall()

        if data is not None:
            dataPackage = []
            for row in data:
                dataPackage.append({"epoch": row[1], "actionType": row[2], "comment": row[3]})

            return dataPackage
        else:
            return None
