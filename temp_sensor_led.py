import RPi.GPIO as GPIO

class RgbLed:
    def __init__(self, pins):
        GPIO.setmode(GPIO.BOARD)

        self.RED_PIN = pins["red"]
        self.GREEN_PIN = pins["green"]
        self.BLUE_PIN = pins["blue"]

        self.__setup_pins()
    
    def __setup_pins(self):
        GPIO.setup(self.RED_PIN, GPIO.OUT)
        GPIO.setup(self.GREEN_PIN, GPIO.OUT)
        GPIO.setup(self.BLUE_PIN, GPIO.OUT)

        # default state is GREEN ON
        self.__update_gpio_output(1, 0, 1)

    def __update_gpio_output(self, red_output, green_output, blue_output):
        # 0 = on
        # 1 = off

        GPIO.output(self.RED_PIN, red_output)
        GPIO.output(self.GREEN_PIN, green_output)
        GPIO.output(self.BLUE_PIN, blue_output)

    def update_color(self, temp_status):
        status = temp_status.upper()

        if status == "ABOVE":
            # set LED color to WHITE
            self.__update_gpio_output(0, 0, 0)
        elif status == "BELOW":
            # set LED color to BLUE
            self.__update_gpio_output(1, 1, 0)
        elif status == "WITHIN":
            # set LED color to GREEN
            self.__update_gpio_output(1, 0, 1)
        elif status == "ERROR":
            # set LED color to RED
            self.__update_gpio_output(0, 1, 1)
        else:
            print("\n!!!!!!!!!!\n-> ERROR: Unknown temp status command.\n-> Turning LEDs off.\n!!!!!!!!!!\n")
            self.__update_gpio_output(1, 1, 1)
