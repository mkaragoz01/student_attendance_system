import RPi.GPIO as GPIO
import time 

def led():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11,GPIO.OUT)
    GPIO.output(11,GPIO.HIGH)
    time.sleep(0.8)
    GPIO.output(11,GPIO.LOW)
