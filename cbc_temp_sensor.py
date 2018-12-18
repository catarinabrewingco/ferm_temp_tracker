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

# gets the temps from each temperature file in the given list
def getTemps(tempSensorFiles = []):
    temps = []

    #for file in tempSensorFiles:
    for entry in tempSensorFiles:
        file = entry['tempSensorFile']
        rawTemp = getRawTempData(file)

        # if the temperature line is present
        if rawTemp.find('t=') != -1:
            # get the digits (actual temp in Celsius) after the 't='
            tempData = rawTemp[rawTemp.find('t=') + 2:]
            # get temperature in Fahrenheit
            tempFahrenheit = getTempInFahrenheit(tempData)
            # round to two decimal places
            tempFahrenheitRounded = round(tempFahrenheit, 2)
            # add it to the temps list
            temps.append({'tempSensorId': entry['tempSensorId'], 'temp': tempFahrenheitRounded})

    return temps

# gets raw temperature data line from given file
def getRawTempData(file):
    lines = readFile(file)

    # if the first line does not read affirmative...
    while lines[0].strip()[-3:] != 'YES':
        # the probe is not reading properly; wait, then try again
        time.sleep(0.2)
        lines = readFile(file)

    # return just the temperature line from the file
    return lines[1]

# reads the given file, then closes the file and returns the lines from it
def readFile(file):
    currentFile = open(file, 'r')
    lines = currentFile.readlines()
    currentFile.close()

    return lines

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

# main loop for the program
def run():
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
        
            # infinite loop to attempt to run the program
            while True:
                # get the temperature (in Fahrenheit) from each temp sensor
                temps = getTemps(files)

                # print out each sensor's ID, timestamp, and temp data
                for temp in temps:
                    print('probe: {} | datetime: {} | temp (F): {}'.format(temp['tempSensorId'], getDateTime(), temp['temp']))

                # line delimiter
                print('--------')

                # wait interval
                time.sleep(0.5)
                
    # if no sensors are detected, kill the program
    except NoSensorsDetectedException:
        print("\n!!!!!\n-> No temp sensors detected.\n-> Exiting program.\n!!!!!\n")
        # kills the program
        exit()
    
    # if Crtl+C is pressed on the keyboard, kill the program
    except KeyboardInterrupt:
        print("\n!!!!!\n-> Keyboard interrupt has been triggered.\n-> Exiting program.\n!!!!!\n")
        # kills the program
        exit()
        
    # if an error is detected, kill the program
    except:
        print("\n!!!!!\n-> An unknown error has occurred.\n-> Exiting program.\n!!!!!\n")
        # kills the program
        exit()
        
# custom exception class for when no sensors are detected
class NoSensorsDetectedException(Exception):
    pass

# run the program on the main thread
if __name__ == '__main__':
    run()
