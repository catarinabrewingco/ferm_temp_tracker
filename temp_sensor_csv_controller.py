import csv
import datetime
import os.path

class CsvController:
    LOGS_DIRECTORY = "logs"
    CSV_DIRECTORY = "csv"

    def __init__(self):
        self.FILEPATH = self.__set_filepath()
        self.__set_headers()

    def __set_filepath(self):
        filename = "ferm_temp_data_log_{}.csv".format(self.__get_datetime())
        return os.path.join(self.LOGS_DIRECTORY, self.CSV_DIRECTORY, filename)

    def __set_headers(self):
        with open(self.FILEPATH, 'w') as csv_file:
            row = [
                "Sensor Name",
                "Sensor Position",
                "Sensor ID",
                "Timestamp",
                "Recorded Temp",
                "Target Temp",
                "Allowed Temp Range",
                "Highest Recorded Temp",
                "Lowest Recorded Temp",
                "% Spent Above Temp Range",
                "% Spent Within Temp Range",
                "% Spent Below Temp Range",
                "% Spent in Error State",
                "Error"
            ]

            writer = csv.writer(csv_file)
            writer.writerow(row)

    # gets the current date and time in format MonthDayYear_Hour-Minute-Seconds
    # (e.g. Dec-17-2018_04-32-56)
    def __get_datetime(self):
        current_date_time = datetime.datetime.now()
        return current_date_time.strftime("%b-%d-%Y_%I-%M-%S")

    def append_sensor_data_to_file(self, sensor):
        with open(self.FILEPATH, 'a') as csv_file:
            temp_data = sensor.get_latest_recorded_temp_data()
            row = [
                sensor.NAME,
                sensor.POSITION,
                sensor.ID,
                temp_data.DATETIME,
                temp_data.TEMP_IN_FAHRENHEIT,
                sensor.TARGET_TEMP,
                "{}-{}".format(sensor.TARGET_TEMP - sensor.TARGET_TEMP_NEGATIVE_ALLOWANCE, sensor.TARGET_TEMP + sensor.TARGET_TEMP_POSITIVE_ALLOWANCE),
                sensor.highest_temp,
                sensor.lowest_temp,
                sensor.percentage_spent_above_target_temp_range,
                sensor.percentage_spent_within_target_temp_range,
                sensor.percentage_spent_below_target_temp_range,
                sensor.percentage_spent_in_error_state,
                sensor.ERROR
            ]

            writer = csv.writer(csv_file)
            writer.writerow(row)