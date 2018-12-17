import os
import glob
import time
import datetime

# start the required modules to read the sensor data
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

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

def getDateTime():
    currentDateTime = datetime.datetime.now()

    return currentDateTime.strftime('%a, %b %d, %Y %I:%M:%S %p')

# main loop for the program
def run():
    print('we are running...')
    files = getTempSensorFiles()
    print('we have a number of files...')
    
    while True:
        temps = getTemps(files)

        for temp in temps:
            print('probe: {} | datetime: {} | temp (F): {}'.format(temp['tempSensorId'], getDateTime(), temp['temp']))

        print('--------')

        # wait interval
        time.sleep(0.5)

if __name__ == '__main__':
    run()
