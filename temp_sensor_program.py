import traceback
import time
from temp_sensor_controller import TempSensorController as Controller
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

# !!! NOTE !!!
# Are you having trouble running this script, though when last it was run all was working?
# Make sure your command line is > python3 {name of this script}.py
# NOT > python {name of this script}.py
# There are input() inconsistencies between Python 2 and Python 3+, so make sure you're using latest
    # by using the command for python3 (if on Raspberry Pi 3 B+, anyway)
# !!! END NOTE !!!

LED_PIN_SETS = [
    {"red": 11, "green": 13, "blue": 15}
]

# sets the polling rate between temp recordings
def set_polling_rate():
    while True:
        try:
            requested_time = int(input("\n----------\n-> How often (in minutes) would you like temperatures recorded? "))
        except ValueError:
            print("----------\n!!! Sorry, you must enter an integer. Try again.\n----------")
            continue
        if requested_time < 2:
            print("-> The minimum required polling rate is 2 minutes.\n-> Setting polling rate to 2 minutes.\n----------\n")
            return 2 * 60
        else:
            print("-> Polling minutes accepted.\n-> Monitoring temperatures every {} minutes starting now.\n----------\n".format(requested_time))
            return round(requested_time * 60, 2)

# run the main program
def run():
    try:
        print("----------\n-> Program running.\n-> Searching for temp sensors...\n----------")

        # instantiate controller obj (which also detects all available sensors)
        controller = Controller(LED_PIN_SETS)

        # ask the user how long they would like the wait to be between recording temperatures
        polling_rate = set_polling_rate()

        while True:
            print("\n-> Polling sensors...")
            controller.get_temps()
            time.sleep(polling_rate)
        
    # if Crtl+C is pressed on the keyboard, kill the program
    except KeyboardInterrupt:
        print("\n!!!!!!!!!!\n-> Keyboard interrupt has been triggered.\n-> Exiting program.\n!!!!!!!!!!\n")
        traceback.print_exc()
        GPIO.cleanup()
        # kills the program
        exit()
        
    # if an unexpected error is detected, kill the program
    except Exception as e:
        print("\n!!!!!!!!!!\n-> A(n) {} error has occurred.\n-> Exiting program.\n!!!!!!!!!!\n".format(e.__class__.__name__))
        traceback.print_exc()
        GPIO.cleanup()
        # kills the program
        exit()

# run the program on the main thread
if __name__ == "__main__":
    run()