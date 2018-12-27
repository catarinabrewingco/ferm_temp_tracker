import time
import datetime
import sys
sys.path.append("..")
from helpers.temp_sensor_led import RgbLed

class TempSensor:
    FILE_NOT_FOUND = "FILE NOT FOUND"
    NO_SUCCESSFUL_TEMP = "NO SUCCESSFUL TEMP READING"
    FILE_EMPTY = "FILE EMPTY"

    # each sensor will be init'd with a user-given name, and an assigned position
    # based off of the sensor's directory id value, eg 28-0*
    def __init__(self, name, position, id, target_temp, target_temp_positive_allowance, target_temp_negative_allowance, led_pins):
        self.NAME = name
        self.POSITION = position
        self.ID = id
        self.FILE = "/sys/bus/w1/devices/{}/w1_slave".format(self.ID)
        self.ERROR = None
        self.TARGET_TEMP = target_temp
        self.TARGET_TEMP_POSITIVE_ALLOWANCE = target_temp_positive_allowance
        self.TARGET_TEMP_NEGATIVE_ALLOWANCE = target_temp_negative_allowance
        self.highest_temp = None
        self.lowest_temp = None
        self.above_target_temp_range = []
        self.within_target_temp_range = []
        self.below_target_temp_range = []
        self.in_error_state = []
        self.percentage_spent_above_target_temp_range = None
        self.percentage_spent_within_target_temp_range = None
        self.percentage_spent_below_target_temp_range = None
        self.percentage_spent_in_error_state = None
        self.recorded_temp_data = []

        if led_pins != None:
            self.LED = RgbLed(led_pins)
            self.HAS_LED = True
        else:
            self.LED = None
            self.HAS_LED = False

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
        # default temp data is 0.0 for an error state, only to be updated
        # below if a proper temp is found
        temp = 0.0

        # if raw_temp is not empty and it contains a "t=" string (temp indicator)
        if len(raw_temp) > 0 and raw_temp.find("t=") != -1:
            # get the temp in celsius, then convert it to fahrenheit
            temp_celsius = raw_temp[raw_temp.find("t=") + 2:]
            temp_fahrenheit = round(self.__convert_temp_to_fahrenheit(temp_celsius), 2)

            # if the temp in fahrenheit does not exceed 110 and is not 0.0, eg is not an error temp
            # (ds18b20 probes return high 100 F temps when erring sometimes)
            if temp_fahrenheit < 110 and temp_fahrenheit != 0.0:
                # set the temp equal to the temp_fahrenheit
                temp = temp_fahrenheit
            else:
                self.ERROR = self.__set_error(self.NO_SUCCESSFUL_TEMP)
        
        # update the recorded temp data array with the given timestamp and final temp
        self.__update_recorded_temp_data(timestamp, temp)

    # extracts the raw temperature data from the associated w1_slave file
    # or returns an empty array if the file cannot be found
    def __get_raw_temp_data(self):
        lines = self.__read_file()

        # if there are lines, then the file was (at least) present
        if len(lines) > 0:
            # but we need to verify now that it is reading temps
            # if the first line doesn't end in YES, then we
            # have a sensor error of some sort, which could be
            # an internal error in the probe, or a disconnect that
            # happened outside of the ~90 second detection zone
            if lines[0].strip()[-3:] != "YES":
                print("\n!! -> Hmmm...sensor named {} at position {} is not reporting temperatures correctly.".format(self.NAME, self.POSITION))
                tries = 1
                max_tries = 5

                # retry reading the file to see if a proper temp is reported
                while tries <= max_tries:
                    print("\n!! -> Attempting to read file again...attempt {} of {}".format(tries, max_tries))
                    lines = self.__read_file()
                    # if the file is still not empty
                    if len(lines) > 0:
                        # check again to see if a temp is being reported
                        if lines[0].strip()[-3:] != "YES":
                            # if not, increase our tries counter, wait a couple seconds,
                            # then try again
                            tries += 1
                            time.sleep(2)
                            continue
                        # if we got a successful temp reported, return it
                        else:
                            print("\n----------\n-> File reading now successful for sensor named {} at position {}.\n-> Continuing...\n----------\n".format(self.NAME, self.POSITION))
                            return lines[1]
                    # if the file is now empty, return an empty array (error state)
                    else:
                        if self.ERROR == None:
                            print("\n!! -> File for sensor named {} at position {}  may have been empty after retrying.\n!! -> Continuing with its temp reporting at 0.0 degrees F.".format(self.NAME, self.POSITION))
                            self.ERROR = self.__set_error(self.FILE_EMPTY)
                        return []
                # if we were never successful in getting a temp reported
                # and the file was never empty, return an empty array (error state)
                if self.ERROR == None:
                    print("\n!! -> Couldn't find a successful temp reading for sensor named {} at position {}.\n!! -> Continuing with its temp reporting at 0.0 degrees F.".format(self.NAME, self.POSITION))
                    self.ERROR = self.__set_error(self.NO_SUCCESSFUL_TEMP)

                return []
            # if the file's first line ended in YES, it is reporting a temp reading
            # return that reading for analysis
            return lines[1]
        # if the file was empty, return an empty array (error state)
        else:
            if self.ERROR == None:
                print("\n!! -> File for sensor named {} at position {} was empty.\n!! -> Continuing with its temp reporting at 0.0 degrees F.".format(self.NAME, self.POSITION))
                self.ERROR = self.__set_error(self.FILE_EMPTY)
            
            return []

    # returns the lines from the associated w1_slave file
    # or returns an empty array if the file cannot be found
    def __read_file(self):
        try:
            with open(self.FILE, "r") as data_file:
                self.ERROR = None
                return data_file.readlines()
        
        except IOError:
            print("\n!!!!!!!!!!" +
                "\n-> Uh oh, file for sensor named {} at position {} no longer found.".format(self.NAME, self.POSITION) +
                "\n-> Continuing with its temp reporting at 0.0 degrees F." +
                "\n-> Please check its connections." +
                "\n!!!!!!!!!!\n"
            )
            self.ERROR = self.__set_error(self.FILE_NOT_FOUND)

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
        self.__update_percentage_spent_lists(temp_fahrenheit)

        # if the temperature successfully recorded, also update highest/lowest
        if temp_fahrenheit != 0.0:
            self.__update_highest_and_lowest_temps(temp_fahrenheit)

    def __update_highest_and_lowest_temps(self, latest_temp):
        if self.highest_temp == None:
            self.highest_temp = latest_temp
        elif self.highest_temp < latest_temp:
            self.highest_temp = latest_temp

        if self.lowest_temp == None:
            self.lowest_temp = latest_temp
        elif self.lowest_temp > latest_temp:
            self.lowest_temp = latest_temp

    def __update_percentage_spent_lists(self, latest_temp):
        total_entries = len(self.recorded_temp_data)
        positive_range = self.TARGET_TEMP + self.TARGET_TEMP_POSITIVE_ALLOWANCE
        negative_range = self.TARGET_TEMP - self.TARGET_TEMP_NEGATIVE_ALLOWANCE

        # if the sensor is in an error state
        if latest_temp == 0.0:
            self.in_error_state.append(latest_temp)
            self.__try_update_led("ERROR")
        # if the temp is below the allowed minimum (target temp - negative allowance)
        elif latest_temp < negative_range:
            self.below_target_temp_range.append(latest_temp)
            self.__try_update_led("BELOW")
        # if the temp is above the allowed maximum (target temp + positive allowance)
        elif latest_temp > positive_range:
            self.above_target_temp_range.append(latest_temp)
            self.__try_update_led("ABOVE")
        # if the temp is within the allowed range of temps
        elif latest_temp >= negative_range and latest_temp <= positive_range:
            self.within_target_temp_range.append(latest_temp)
            self.__try_update_led("WITHIN")

        below_entries = len(self.below_target_temp_range)
        above_entries = len(self.above_target_temp_range)
        within_entries = len(self.within_target_temp_range)
        error_entries = len(self.in_error_state)

        self.percentage_spent_below_target_temp_range = round(below_entries / total_entries * 100, 2)
        self.percentage_spent_above_target_temp_range = round(above_entries / total_entries * 100, 2)
        self.percentage_spent_within_target_temp_range = round(within_entries / total_entries * 100, 2)
        self.percentage_spent_in_error_state = round(error_entries / total_entries * 100, 2)

    def __set_error(self, error_type):
        return "File error: {}.\nPlease check connections for this sensor.".format(error_type)

    def __try_update_led(self, color):
        if self.LED != None:
            self.LED.update_color(color)


# class to represent a given temperature recording's data set, including a timestamp and
# temperature in Fahrenheit, rounded to two decimal places
class TempData:
    def __init__(self, datetime = None, temp_in_fahrenheit = None):
        self.DATETIME = datetime
        self.TEMP_IN_FAHRENHEIT = temp_in_fahrenheit