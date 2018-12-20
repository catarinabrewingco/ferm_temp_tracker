import time
import datetime

class TempSensor:
    # each sensor will be init'd with a user-given name, and an assigned position
    # based off of the sensor's directory id value, eg 28-0*
    def __init__(self, name, position, id):
        self.NAME = name
        self.POSITION = position
        self.ID = id
        self.FILE = "/sys/bus/w1/devices/{}/w1_slave".format(self.ID)
        self.ERROR = None
        self.recorded_temp_data = []

    def get_latest_recorded_temp_data(self):
        if len(self.recorded_temp_data) > 0:
            return self.recorded_temp_data[-1]
        else:
            return TempData()

    # will print out all recorded temp data for this sensor
    def print_all_recorded_temp_data(self):
        print("Recorded temp data for sensor named {} at position {}:".format(self.NAME, self.POSITION))
        for data_set in self.recorded_temp_data:
            print("timestamp: {}, temperature: {}".format(data_set.DATETIME, data_set.TEMP_IN_FAHRENHEIT))

    # gets the current temperature data in Fahrenheit, rounded to two decimal places,
    # at the time of the given timestamp (for consistency w/ other sensor readings)
    def get_temp_at(self, timestamp):
        raw_temp = self.__get_raw_temp_data()

        if len(raw_temp) > 0 and raw_temp.find("t=") != -1:
            temp_celsius = raw_temp[raw_temp.find("t=") + 2:]
            temp_fahrenheit = round(self.__convert_temp_to_fahrenheit(temp_celsius), 2)

            self.__update_recorded_temp_data(timestamp, temp_fahrenheit)
        else:
            self.__update_recorded_temp_data(timestamp, 0.0)

    # extracts the raw temperature data from the associated w1_slave file
    # or returns an empty array if the file cannot be found
    def __get_raw_temp_data(self):
        lines = self.__read_file()

        if len(lines) > 0:
            while lines[0].strip()[-3:] != "YES":
                time.sleep(0.5)
                lines = self.__read_file()
            return lines[1]
        else:
            return []
        

    # returns the lines from the associated w1_slave file
    # or returns an empty array if the file cannot be found
    def __read_file(self):
        try:
            data_file = open(self.FILE, "r")
            lines = data_file.readlines()
            data_file.close()
            self.ERROR = None

            return lines
        
        except IOError:
            print("\n!!!!!!!!!!" +
                "\n-> Uh oh, file for sensor named {} at position {} no longer found.".format(self.NAME, self.POSITION) +
                "\n-> Continuing with its temp reporting at 0.0 degrees F." +
                "\n-> Please check its connections." +
                "\n!!!!!!!!!!\n"
            )
            self.ERROR = "w1_slave file NOT FOUND. Please check connections for this sensor."

            return []

    # converts the given temp Celsius to temp Fahrenheit
    def __convert_temp_to_fahrenheit(self, temp):
        temp_celsius = float(temp) / 1000.0
        temp_fahrenheit = temp_celsius * 9.0 / 5.0 + 32.0

        return temp_fahrenheit

    # updates the recorded temp data list associated with this sensor, including a timestamp and
    # temperature in Fahrenheit, rounded to two decimal places
    def __update_recorded_temp_data(self, timestamp, temp_fahrenheit):
        self.recorded_temp_data.append(TempData(timestamp, temp_fahrenheit))

# class to represent a given temperature recording's data set, including a timestamp and
# temperature in Fahrenheit, rounded to two decimal places
class TempData:
    def __init__(self, datetime = None, temp_in_fahrenheit = None):
        self.DATETIME = datetime
        self.TEMP_IN_FAHRENHEIT = temp_in_fahrenheit