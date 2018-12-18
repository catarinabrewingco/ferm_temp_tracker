import os
import glob
import time
import datetime

# get all ds18b20 temp sensor directories
tempSensorDirectories = glob.glob('/sys/bus/w1/devices/28*')

# gets a list of temperature sensor files from the directories glob
def getTempSensorFiles():
    tempSensorFiles = []
    
    for dir in tempSensorDirectories:
        tempSensorId = os.path.basename(dir)
        tempSensorFile = dir + '/w1_slave'
        tempSensorFiles.append({'tempSensorId': tempSensorId, 'tempSensorFile': tempSensorFile})
        
    return tempSensorFiles

# gets the temp for the given temperature file
def getTemp(tempSensorFile):
    # set a shorthand for the file
    file = tempSensorFile["tempSensorFile"]
    # attempt to get the raw temperature data from the file
    rawTemp = getRawTempData(file)

    # if we have a rawTemp and it includes the expected line, continue
    if len(rawTemp) > 0 and rawTemp.find("t=") != -1:
        # get just the temperature data (ditching the "t=")
        tempData = rawTemp[rawTemp.find("t=") + 2:]
        # convert the raw temperature data from Celsius (default) to Fahrenheit (desired)
        tempFahrenheit = getTempInFahrenheit(tempData)
        # round the temperature to 2 decimal places
        tempFahrenheitRounded = round(tempFahrenheit, 2)

        # return the final temperature object, which includes the associated probe ID and the Fahrenheit temperature rounded to 2 decimal places
        return {"tempSensorId": tempSensorFile["tempSensorId"], "temp": tempFahrenheitRounded}
    # otherwise, return a temperature object with a 0 temperature recording
    # this will keep the sensor on the chart, indicating to us that it was an unintenional failure
    # whereas once we implement toggle switches (physical and/or digital) for individual probes, that will add/remove probe data from the chart
    else:
        return {"tempSensorId": tempSensorFile["tempSensorId"], "temp": 0.0}

# gets raw temperature data line from given file
def getRawTempData(file):
    # attempt to read the given file
    lines = readFile(file)

    # if the lines array is not empty, read the lines
    if len(lines) > 0:
        # if the first line does not read affirmative...
        while lines[0].strip()[-3:] != 'YES':
            # the probe is not reading properly; wait, then try again
            time.sleep(0.5)
            lines = readFile(file)

        # return just the temperature line from the file
        return lines[1]
    # otherwise, we must not have been able to read the file, so return the empty array given
    else:
        return []

# reads the given file, then closes the file and returns the lines from it
def readFile(file, tries = 0):
    # set a limit to the number of times we can try to find the given file
    max_tries = 5
    
    # if we have yet to exceed our maximum attempts to read the file, do so
    if tries < max_tries:
        # try to read the given file
        try:
            currentFile = open(file, 'r')
            lines = currentFile.readlines()
            currentFile.close()
            
            # if successful, return the lines present in the file
            return lines
        
        # if we cannot find the file, run the method again with an incremented tries counter
        except IOError:
            print("\n!!\n-> Uh oh, couldn't find file {}.\nTries remaining: {}\n!!\n".format(file, max_tries - (tries + 1)))
            readFile(file, tries + 1)

    # if we are unsuccessful in finding the file to read, return an empty array to signal this failure
    return []

# outputs given temperature in Fahrenheit
def getTempInFahrenheit(tempData):
    # convert given data to Celsius
    tempCelsius = float(tempData) / 1000.0
    # convert Celsius to Fahrenheit
    tempFahrenheit = tempCelsius * 9.0 / 5.0 + 32.0

    # return Fahrenheit
    return tempFahrenheit

# get the current date and time in format Day of Week, Month Day, Year Hour:Minute:Seconds AM/PM (e.g. Mon, Dec 17, 2018 04:43:02 PM)
def getDateTime():
    currentDateTime = datetime.datetime.now()
    return currentDateTime.strftime('%a, %b %d, %Y %I:%M:%S %p')

# prints out the temp data from a given list of temps
def print_temps(temps):
    #print out each sensor's ID, timestamp, and temp data
    for temp in temps:
        print('probe: {} | datetime: {} | temp (F): {}'.format(temp['tempSensorId'], getDateTime(), temp['temp']))
        
    # section delimiter
    print("-" * 10)

# main loop for the program
def run():    
    # attempt to run the program!
    try:
        print('-----\n-> Program running.\n-> Searching for temp sensors...\n-----')
        # detect all attached temp sensors
        files = getTempSensorFiles()
        
        # if no sensors are detected, kill the program
        if len(files) < 1:
            raise NoSensorsDetectedException()
        # otherwise, run on!
        else:
            print("\n-----\n-> {} temp sensors detected.\n-> Monitoring temperatures now.\n-----\n".format(len(files)))
            while True:
                temps = []
                
                for file in files:
                    temps.append(getTemp(file))
                    
                print_temps(temps)
                time.sleep(120)
            
    # if no sensors are detected, kill the program
    except NoSensorsDetectedException():
        print("\n!!!!!\n-> No temp sensors detected.\n-> Exiting program.\n!!!!!\n")
        # kills the program
        exit()
        
    # if Crtl+C is pressed on the keyboard, kill the program
    except KeyboardInterrupt:
        print("\n!!!!!\n-> Keyboard interrupt has been triggered.\n-> Exiting program.\n!!!!!\n")
        # kills the program
        exit()
        
    # if an unexpected error is detected, kill the program
    except Exception as e:
        print("\n!!!!!\n-> A(n) {} error has occurred.\n-> Exiting program.\n!!!!!\n".format(e.__class__.__name__))
        # kills the program
        exit()
        
# custom exception class for when no sensors are detected
class NoSensorsDetectedException(Exception):
    pass

# run the program on the main thread
if __name__ == '__main__':
    run()
