import meteo_Handler
import DB_handler
import datetime


class HumiController:

    # class variables

    def __init__(self):

        # variable, if the Controller is running
        self.isRunning = False

        # if the humifier is running (-> relay is closed)
        self.humi_is_Running = False

        self.database_handler = DB_handler.Database_handler()

        # init meteo sensor and do test-ready
        self.meteoSensorHandler = meteo_Handler.meteo_Handler()
        self.meteoSensorHandler.setDevice("0x77")

        temperature, pressure, humidity = self.meteoSensorHandler.readBME280All()

    def getMeteoDataFromSensor(self):

        """ function to retrieve meteo data from the BME280 Sensor"""

        temperature, pressure, humidity = self.meteoSensorHandler.readBME280All()

        # write data into the database
        self.database_handler.addSensorMeasurement({"temp": temperature, "press": pressure, "humi": humidity})

    def analyzeMeteoData(self):

        # get meteodata of the last hour
        timeNow = datetime.datetime.now()

        meteoData = self.database_handler.getMeteoMeasurements((timeNow - (24 * 60 * 60)), timeNow)

        # get latest variables to check
        pass

        # check humidity values
        turn_on_humifier = False
        firstTimeStamp = 0

        for val in meteoData:
            humi = val.get("humi", None)

            if humi is not None and humi < 0.45:
                if firstTimeStamp is 0:
                    # first time of exceedence -> add to firstTimeStamp
                    firstTimeStamp = val.get("epoch", 0)
                else:
                    # check timespan
                    if (val.get("epoch", 0) - firstTimeStamp) > 2.0:
                        turn_on_humifier = True
            else:
                firstTimeStamp = 0

        if turn_on_humifier:
            # -> humifier shoulb be turned on
            self.execAction("On", "humifier", "Humidity drop")

    def execAction(self, action, device, comment):

        pass