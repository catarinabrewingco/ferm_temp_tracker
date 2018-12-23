import os
import glob
import temp_sensor
import traceback
import datetime
from operator import itemgetter
from temp_sensor import TempSensor as TempSensor
from temp_sensor_exceptions import NoSensorsDetectedException

class TempSensorController:
    # when init'd, detect all temp sensor directories
    def __init__(self):
        # self.AVAILABLE_TEMP_SENSORS = self.get_available_temp_sensors()
        self.__select_temp_sensors()

    # main method - gets and prints the temp data from each selected sensor
    def get_temps(self):
        timestamp = self.__get_datetime()

        for sensor in self.__get_selected_temp_sensors():
            sensor.get_temp_at(timestamp)
        self.__print_temp_data()

    # 1. detects all available temperature sensors
    # 2. sorts the list of sensors by directory name (eg ID)
    # 3. returns a list of dicts representing available sensors that includes
    # their position and ID
    def __get_available_temp_sensors(self):
        available_temp_sensor_directories = sorted(glob.glob("/sys/bus/w1/devices/28*"))
        available_temp_sensors = []
        position_counter = 1

        try:
            if len(available_temp_sensor_directories) < 1:
                raise NoSensorsDetectedException()
            else:
                for dir in available_temp_sensor_directories:
                    available_temp_sensors.append(
                        {"position": position_counter, "id": os.path.basename(dir)}
                    )

                    position_counter += 1

                print("-> {} temp sensors found.\n----------".format(len(available_temp_sensors)))
                return available_temp_sensors
        
        # if no sensors are detected, kill the program
        except NoSensorsDetectedException:
            print("\n!!!!!!!!!!\n-> No temp sensors detected.\n-> Exiting program.\n!!!!!!!!!!\n")
            traceback.print_exc()
            # kills the program
            exit()

    # prompt the user to select how many/which of the available temp sensors they
    # want to use
    def __select_temp_sensors(self):
        self.AVAILABLE_TEMP_SENSORS = self.__get_available_temp_sensors()
        num_of_desired_sensors = self.__get_num_of_desired_sensors_from_available()
        target_temp, target_temp_positive_allowance, target_temp_negative_allowance = self.__set_target_temp_info()
        sensor_names = self.__name_sensors(num_of_desired_sensors)
        self.selected_temp_sensors = []

        for sensor in self.AVAILABLE_TEMP_SENSORS[:num_of_desired_sensors]:
            self.selected_temp_sensors.append(
                TempSensor(
                    sensor_names[int(sensor["position"]) - 1],
                    sensor["position"],
                    sensor["id"],
                    target_temp,
                    target_temp_positive_allowance,
                    target_temp_negative_allowance
                )
            )

    # prompt the user for a number of desired sensors to use from the available set
    def __get_num_of_desired_sensors_from_available(self):
        num_of_available_sensors = len(self.AVAILABLE_TEMP_SENSORS)

        while True:
            try:
                num_of_desired_sensors = int(
                    input("-> How many temperature sensors would you like to use from the available {}? ".format(num_of_available_sensors))
                )
            except ValueError:
                print("----------\n!!! Sorry, you must enter an integer. Try again.\n----------")
                continue
            if num_of_desired_sensors < 1:
                print("----------\n!!! Sorry, you must use at least one sensor. Try again.\n----------")
                continue
            if num_of_desired_sensors > num_of_available_sensors:
                print("----------\n!!! Sorry, you cannot use more sensors than are present. Try again.\n----------")
                continue
            else:
                break

        return num_of_desired_sensors

    # sets the target fermentation temperature for the vessels
    def __set_target_temp_info(self):
        while True:
            try:
                target_temp = int(input("-> What is the target fermentation temperature? "))
            except ValueError:
                print("----------\n!!! Sorry, you must enter an integer. Try again.\n----------")
                continue
            else:
                break

        while True:
            try:
                target_temp_positive_allowance = int(input("-> What is the positive allowance above the target fermentation temperature? "))
            except ValueError:
                print("----------\n!!! Sorry, you must enter an integer. Try again.\n----------")
                continue
            else:
                break

        while True:
            try:
                target_temp_negative_allowance = int(input("-> What is the negative allowance below the target fermentation temperature? "))
            except ValueError:
                print("----------\n!!! Sorry, you must enter an integer. Try again.\n----------")
                continue
            else:
                break

        return target_temp, target_temp_positive_allowance, target_temp_negative_allowance

    # prompt the user to assign names to each sensor they selected for use
    def __name_sensors(self, num_of_desired_sensors):
        sensor_names = []
        sensor_counter = 1

        for _ in range(0, num_of_desired_sensors):
            sensor_names.append(
                input("----------\n-> What would you like to name the sensor at position {}? ".format(sensor_counter))
            )
            sensor_counter += 1

        return sensor_names

    # gets the current date and time in format Day of Week, Month Day, Year Hour:Minute:Seconds AM/PM
    # (e.g. Mon, Dec 17, 2018 04:43:02 PM)
    def __get_datetime(self):
        current_date_time = datetime.datetime.now()
        return current_date_time.strftime("%a, %b %d, %Y %I:%M:%S %p")

    # get the list of selected, named temperature sensors
    def __get_selected_temp_sensors(self):
        return self.selected_temp_sensors

    # prints the latest temp data per sensor
    def __print_temp_data(self):
        print("=" * 10)
        print("-" * 5)
        for sensor in self.__get_selected_temp_sensors():
            temp_data = sensor.get_latest_recorded_temp_data()

            if sensor.ERROR == None:
                print("NAME: {}\nPOSITION: {}\nLATEST TIMESTAMP: {}\nLATEST TEMP (F): {}\nTARGET TEMP (F): {}\nALLOWED TEMP RANGE (F): {}-{}\nHIGHEST TEMP (F): {}\nLOWEST TEMP (F): {}\n% SPENT ABOVE TEMP RANGE: {}\n% SPENT BELOW TEMP RANGE: {}\n% SPENT WITHIN TEMP RANGE: {}\n% SPENT IN ERROR STATE: {}".format(
                    sensor.NAME,
                    sensor.POSITION,
                    temp_data.DATETIME,
                    temp_data.TEMP_IN_FAHRENHEIT,
                    sensor.TARGET_TEMP,
                    sensor.TARGET_TEMP - sensor.TARGET_TEMP_NEGATIVE_ALLOWANCE,
                    sensor.TARGET_TEMP + sensor.TARGET_TEMP_POSITIVE_ALLOWANCE,
                    sensor.highest_temp,
                    sensor.lowest_temp,
                    sensor.percentage_spent_above_target_temp_range,
                    sensor.percentage_spent_below_target_temp_range,
                    sensor.percentage_spent_within_target_temp_range,
                    sensor.percentage_spent_in_error_state
                ))
            else:
                print("!!!!!!!!!!\nERROR: {}\n!!!!!!!!!!\nNAME: {}\nPOSITION: {}\nLATEST TIMESTAMP: {}\nLATEST TEMP (F): {}".format(
                    sensor.ERROR,
                    sensor.NAME,
                    sensor.POSITION,
                    temp_data.DATETIME,
                    temp_data.TEMP_IN_FAHRENHEIT
                ))
            print("-" * 5)
        print("=" * 10)