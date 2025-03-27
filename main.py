import pyautogui as pg
import time

time.sleep(2)   

def bufs():
    while True:
        pg.PAUSE = 1.5
        pg.press('f1')
        pg.press('f2')
        pg.press('f3')
        pg.press('f4')
        pg.press('f9')
        pg.press('f10')
        time.sleep(160)

bufs()
