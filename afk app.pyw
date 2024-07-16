import keyboard
from time import sleep
from ctypes import windll, create_unicode_buffer
from datetime import datetime
from pywinauto import Desktop
from tkinter import *

app_exclusion = ["", "Taskbar", "Program Manager"]

class Main:
    def __init__(self):
        # Initialising and setting up root window
        self.root = Tk()
        self.root.geometry("720x600")
        self.root.resizable(False, False)
        self.root.title("AFK App")

        # Font styles
        self.font_container = ("Times New Roman", "11")
        self.font_heading = ("Helvetica", "12", "bold")

        self.afk = False # Controlled by afk start/stop button
        self.keys = None # Changed when key presses are recorded for afk playback
        self.app = ""
        
        # Frame to hold applist and related widgets
        self.frame_apps = Frame(self.root, padx=10, pady=10)
        self.frame_apps.grid(column=0, row=0)
        # Label for list of windows/apps
        Label(self.frame_apps, text="Windows", font=self.font_heading).grid(row=0, sticky=W)
        # Creating and populating listbox containing apps
        self.listbox_apps = Listbox(self.frame_apps, width=40, font=self.font_container) # Create listbox to allow user to select app
        self.updateAppsList()
        self.listbox_apps.grid(row=1, pady=5) # Place listbox in root window
        # Button to refresh apps/windows list
        Button(self.frame_apps, text="REFRESH LIST", command=self.updateAppsList, width=40).grid(row=2)

    def start(self):
        self.root.mainloop()

    def updateAppsList(self):
        global app_exclusion

        # If the list of application actually has content
        self.listbox_apps.delete('0', 'end') # Clear list

        windows = [w.window_text() for w in Desktop(backend="uia").windows()] # active windows (static)
        # Loop through applications and insert at bottom of listbox
        for window in windows:
            if window not in app_exclusion and window != self.root.title():
                self.listbox_apps.insert(-1, window)

        # Scroll to top of list, forces update to listbox display
        self.listbox_apps.yview_moveto(0)

    def getForegroundWindow(self):
        hWnd = windll.user32.GetForegroundWindow()
        length = windll.user32.GetWindowTextLengthW(hWnd)
        buf = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hWnd, buf, length + 1)
        return buf.value if buf.value else "None"

# def closeLoop():
#     global runLoop
#     global running
#     print("Ending application")
#     runLoop = False
#     running = False

# def pauseLoop():
#     global running
#     nowTime = datetime.now()
#     currTime = nowTime.strftime("%H:%M:%S")
#     paused = " # " + ("Paused" if running else "Unpaused")
#     print(currTime + paused)
#     running = False if running else True

# keyboard.add_hotkey('F2', closeLoop, suppress=True) # End app
# keyboard.add_hotkey('F3', pauseLoop, suppress=True) # Pause app

# windows = [w.window_text() for w in Desktop(backend="uia").windows()]
# windows.remove("Taskbar")
# windows.remove("Program Manager")


# root = Tk()
# root.geometry("600x600")


# if __name__ == "__main__":
#     root.mainloop()
#     app = input("enter app name: ")
#     while runLoop:
#         sleep(2)
#         while running:
#             if getForegroundWindow() != app:
#                 pauseLoop()
#                 break
#             keyboard.press(keyPress)
#             sleep(0.3)
#             keyboard.release(keyPress)
#             sleep(1.5)

if __name__ == "__main__":

    app = Main()
    app.start()