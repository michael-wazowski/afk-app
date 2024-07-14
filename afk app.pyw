import keyboard
import time
from ctypes import windll, create_unicode_buffer
from datetime import datetime
from pywinauto import Desktop
from tkinter import *

runLoop = True
running = True
keyPress = 'space'

def getForegroundWindow():
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    return buf.value if buf.value else "None"

def closeLoop():
    global runLoop
    global running
    print("Ending application")
    runLoop = False
    running = False

def pauseLoop():
    global running
    nowTime = datetime.now()
    currTime = nowTime.strftime("%H:%M:%S")
    paused = " # " + ("Paused" if running else "Unpaused")
    print(currTime + paused)
    running = False if running else True

keyboard.add_hotkey('F2', closeLoop, suppress=True) # End app
keyboard.add_hotkey('F3', pauseLoop, suppress=True) # Pause app

windows = [w.window_text() for w in Desktop(backend="uia").windows()]
windows.remove("Taskbar")
windows.remove("Program Manager")


root = Tk()
root.geometry("600x600")


if __name__ == "__main__":
    root.mainloop()
    # app = input("enter app name: ")
    # while runLoop:
    #     time.sleep(2)
    #     while running:
    #         if getForegroundWindow() != app:
    #             pauseLoop()
    #             break
    #         keyboard.press(keyPress)
    #         time.sleep(0.3)
    #         keyboard.release(keyPress)
    #         time.sleep(1.5)