import json
import datetime
import os.path

class JsonController:
    LOGS_DIRECTORY = "logs"
    JSON_DIRECTORY = "json"

    def __init__(self, sensors):
        self.FILEPATH = self.__set_filepath()
        self.__create_file(sensors)

    def __set_filepath(self):
        filename = "ferm_temp_data_log_{}.json".format(self.__get_datetime())

        # try to make the subdirectories, if not found
        os.makedirs("{}/{}".format(self.LOGS_DIRECTORY, self.JSON_DIRECTORY), exist_ok=True)

        return os.path.join(self.LOGS_DIRECTORY, self.JSON_DIRECTORY, filename)

    # gets the current date and time in format MonthDayYear_Hour-Minute-Seconds
    # (e.g. Dec-17-2018_04-32-56)
    def __get_datetime(self):
        current_date_time = datetime.datetime.now()
        return current_date_time.strftime("%b-%d-%Y_%I-%M-%S")

    def __create_file(self, sensors):
        # create the initial json file w/ each sensor
        sensors_array = []

        for sensor in sensors:            
            sensors_array.append(self.__set_initial_serializable_sensor_dict(sensor))

        self.__write_to_json_file(sensors_array)

    # instantiates the initial objects for the current json file's dataset
    def __set_initial_serializable_sensor_dict(self, sensor):
        # return a serializable dict for the given sensor
        return {
            "Sensor Name": sensor.NAME,
            "Sensor Position": sensor.POSITION,
            "Sensor ID": sensor.ID,
            "Sensor Data": {
                "Recorded Temp Data": [],
                "Target Temp": sensor.TARGET_TEMP,
                "Allowed Temp Range": "{}-{}".format(
                    sensor.TARGET_TEMP - sensor.TARGET_TEMP_NEGATIVE_ALLOWANCE,
                    sensor.TARGET_TEMP + sensor.TARGET_TEMP_POSITIVE_ALLOWANCE
                ),
                "Highest Recorded Temp": sensor.highest_temp,
                "Lowest Recorded Temp": sensor.lowest_temp,
                "% Spent Above Temp Range": sensor.percentage_spent_above_target_temp_range,
                "% Spent Within Temp Range": sensor.percentage_spent_within_target_temp_range,
                "% Spent Below Temp Range": sensor.percentage_spent_below_target_temp_range,
                "% Spent in Error State": sensor.percentage_spent_in_error_state
            }
        }
    
    # gets the latest recorded temperature data from the given sensor
    # to update the sensor dict accordingly in our json file
    def __get_updated_latest_recorded_temp_data(self, sensor):
        latest_recorded_temp_data = sensor.get_latest_recorded_temp_data()
        return {
            "Timestamp": latest_recorded_temp_data.DATETIME,
            "Temp (in Fahrenheit)": latest_recorded_temp_data.TEMP_IN_FAHRENHEIT
        }

    # reads the current json file into a useable Python dict
    def __get_json_data(self):
        try:
            with open(self.FILEPATH, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print("!!! -> JSON Read File Error: FILE NOT FOUND: {}".format(self.FILEPATH))
            # need to do something more elegant here than pass?
            pass
        except Exception as e:
            print("!!! -> JSON Read File Error: {}".format(e))
            # need to do something more elegant here than pass?
            pass

    # writes the given dataset into the current json file
    # sorted, and with pretty printing
    def __write_to_json_file(self, data):
        try:
            with open(self.FILEPATH, 'w') as json_file:
                json.dump(data, json_file, indent=4, sort_keys=True)

        except Exception as e:
            print("!!! -> JSON Write File Error: {}".format(e))
            # need to do something more elegant here than pass?
            pass

    # updates the corresponding object in the read json dataset
    # with the appropriate fields that may have updated between readings
    def update_sensor_data(self, sensor):
        data = self.__get_json_data()
        latest_recorded_temp_data = self.__get_updated_latest_recorded_temp_data(sensor)

        # search through the given dataset
        for sensor_dict in data:
            # when we find the matching sensor dict for the given sensor
            if sensor_dict["Sensor Name"] == sensor.NAME:
                # get a variable for the Sensor Data object that needs updating
                sensor_data = sensor_dict["Sensor Data"]

                # update the necessary fields
                sensor_data["Recorded Temp Data"].append(latest_recorded_temp_data)
                sensor_data["Highest Recorded Temp"] = sensor.highest_temp
                sensor_data["Lowest Recorded Temp"] = sensor.lowest_temp
                sensor_data["% Spent Above Temp Range"] = sensor.percentage_spent_above_target_temp_range
                sensor_data["% Spent Within Temp Range"] = sensor.percentage_spent_within_target_temp_range
                sensor_data["% Spent Below Temp Range"] = sensor.percentage_spent_below_target_temp_range
                sensor_data["% Spent in Error State"] = sensor.percentage_spent_in_error_state

        # overwrite the file with the newly updated dataset
        self.__write_to_json_file(data)