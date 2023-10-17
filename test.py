from pynput.keyboard import Key, Controller
import time 


keyboard = Controller()
while 1:
    keyboard.press('a')
    keyboard.release('a')
    time.sleep(1)
