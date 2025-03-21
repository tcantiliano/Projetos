import pyautogui as pg
import time 

time.sleep(1)


def pressKey():
    pg.PAUSE = 2
    pg.press('num1')
    pg.press('num2')
    print("done")
    
pressKey()

