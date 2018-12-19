import os
import glob
import time
import datetime
from operator import itemgetter

# get all ds18b20 temp sensor directories
temp_sensor_directories = glob.glob("/sys/bus/w1/devices/28*")

# gets a list of temperature sensor files from the directories glob
def get_temp_sensor_files():
    temp_sensor_files = []
    
    for dir in temp_sensor_directories:
        temp_sensor_id = os.path.basename(dir)
        temp_sensor_file = dir + "/w1_slave"
        temp_sensor_files.append({"temp_sensor_id": temp_sensor_id, "temp_sensor_file": temp_sensor_file})

    # sort the probes by ascending order by their ID fields
    return sorted(temp_sensor_files, key=itemgetter("temp_sensor_id"))

# gets the temp for the given temperature file
def get_temp(temp_sensor_file):
    # set a shorthand for the file
    file = temp_sensor_file["temp_sensor_file"]
    # attempt to get the raw temperature data from the file
    raw_temp = get_raw_temp_data(file)

    # if we have a raw_temp and it includes the expected line, continue
    if len(raw_temp) > 0 and raw_temp.find("t=") != -1:
        # get just the temperature data (ditching the "t=")
        temp_data = raw_temp[raw_temp.find("t=") + 2:]
        # convert the raw temperature data from Celsius (default) to Fahrenheit (desired)
        temp_fahrenheit = get_temp_in_fahrenheit(temp_data)
        # round the temperature to 2 decimal places
        temp_fahrenheit_rounded = round(temp_fahrenheit, 2)

        # return the final temperature object, which includes the associated probe ID and the Fahrenheit temperature rounded to 2 decimal places
        return {"temp_sensor_id": temp_sensor_file["temp_sensor_id"], "temp": temp_fahrenheit_rounded}
    # otherwise, return a temperature object with a 0 temperature recording
    # this will keep the sensor on the chart, indicating to us that it was an unintenional failure
    # whereas once we implement toggle switches (physical and/or digital) for individual probes, that will add/remove probe data from the chart
    else:
        return {"temp_sensor_id": temp_sensor_file["temp_sensor_id"], "temp": 0.0}

# gets raw temperature data line from given file
def get_raw_temp_data(file):
    # attempt to read the given file
    lines = read_file(file)

    # if the lines array is not empty, read the lines
    if len(lines) > 0:
        # if the first line does not read affirmative...
        while lines[0].strip()[-3:] != "YES":
            # the probe is not reading properly; wait, then try again
            time.sleep(0.5)
            lines = read_file(file)

        # return just the temperature line from the file
        return lines[1]
    # otherwise, we must not have been able to read the file, so return the empty array given
    else:
        return []

# reads the given file, then closes the file and returns the lines from it
def read_file(file):
    # try to read the given file
    try:
        current_file = open(file, "r")
        lines = current_file.readlines()
        current_file.close()
        
        # if successful, return the lines present in the file
        return lines
    
    # if we cannot find the file, run the method again with an incremented tries counter
    except IOError:
        print("\n!!!!!!!!!!" +
              "\n-> Uh oh, file {} no longer found.".format(file) +
              "\n-> Continuing with its temp reporting at 0.0 degrees F." +
              "\n-> Please check its connections." +
              "\n!!!!!!!!!!\n"
        )

    # if we are unsuccessful in finding the file to read, return an empty array to signal this failure
    return []

# outputs given temperature in Fahrenheit
def get_temp_in_fahrenheit(temp_data):
    # convert given data to Celsius
    temp_celsius = float(temp_data) / 1000.0
    # convert Celsius to Fahrenheit
    temp_fahrenheit = temp_celsius * 9.0 / 5.0 + 32.0

    # return Fahrenheit
    return temp_fahrenheit

# get the current date and time in format Day of Week, Month Day, Year Hour:Minute:Seconds AM/PM (e.g. Mon, Dec 17, 2018 04:43:02 PM)
def get_date_time():
    current_date_time = datetime.datetime.now()
    return current_date_time.strftime("%a, %b %d, %Y %I:%M:%S %p")

# prints out the temp data from a given list of temps
def print_temps(temps):
    #print out each sensor's ID, timestamp, and temp data
    for temp in temps:
        print("probe: {} | datetime: {} | temp (F): {}".format(temp["temp_sensor_id"], get_date_time(), temp["temp"]))
        
    # section delimiter
    print("-" * 10)
   
# sleep for given time
def get_sleep_time():
    requested_time = input("\n----------\n-> How often (in minutes) would you like temperatures recorded? ")
    if requested_time < 2:
        print("-> The minimum required sleep time is 2 minutes.\n-> Setting time to sleep for 2 minutes.\n----------\n")
        return 2 * 60
    else:
        print("-> Polling minutes accepted.\n-> Monitoring temperatures every {} minutes starting now.\n----------\n".format(requested_time))
        return round(requested_time * 60, 2)

# main loop for the program
def run():    
    # attempt to run the program!
    try:
        print("----------\n-> Program running.\n-> Searching for temp sensors...\n----------")
        # detect all attached temp sensors
        files = get_temp_sensor_files()
        
        # if no sensors are detected, kill the program
        if len(files) < 1:
            raise NoSensorsDetectedException()
        # otherwise, run on!
        else:
            print("-> {} temp sensors detected.\n----------\n".format(len(files)))
            
            # ask the user how long they would like the polling wait to be between recording temperatures
            time_to_sleep = get_sleep_time()
            
            # run the loop!
            while True:
                temps = []
                
                print("\n----------\n-> Polling...\n----------")
                
                # get each probe's temperature (and associated ID)
                for file in files:
                    temps.append(get_temp(file))

                # print each probe's ID, datetime (when recorded), and temperature
                print_temps(temps)
                # sleep for the requested (or minimum) amount of time
                time.sleep(time_to_sleep)
            
    # if no sensors are detected, kill the program
    except NoSensorsDetectedException():
        print("\n!!!!!!!!!!\n-> No temp sensors detected.\n-> Exiting program.\n!!!!!!!!!!\n")
        # kills the program
        exit()
        
    # if Crtl+C is pressed on the keyboard, kill the program
    except KeyboardInterrupt:
        print("\n!!!!!!!!!!\n-> Keyboard interrupt has been triggered.\n-> Exiting program.\n!!!!!!!!!!\n")
        # kills the program
        exit()
        
    # if an unexpected error is detected, kill the program
    except Exception as e:
        print("\n!!!!!!!!!!\n-> A(n) {} error has occurred.\n-> Exiting program.\n!!!!!!!!!!\n".format(e.__class__.__name__))
        # kills the program
        exit()
        
# custom exception class for when no sensors are detected
class NoSensorsDetectedException(Exception):
    pass

# run the program on the main thread
if __name__ == "__main__":
    run()
