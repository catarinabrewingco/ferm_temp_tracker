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
        GPIO.output(self.RED_PIN, 1)
        GPIO.output(self.GREEN_PIN, 0)
        GPIO.output(self.BLUE_PIN, 1)

    def update_color(self, temp):
        pass