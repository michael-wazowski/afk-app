import keyboard
from time import sleep
from ctypes import windll, create_unicode_buffer
from datetime import datetime
from pywinauto import Desktop
from tkinter import *
from tkinter import messagebox

app_exclusion = ["", "Taskbar", "Program Manager"]

class Main:
    def __init__(self):
        # Initialising and setting up root window
        self.root = Tk()
        self.root.geometry("735x600")
        self.root.resizable(False, False)
        self.root.title("AFK App")

        # Font styles
        self.font_container = ("Times New Roman", "11")
        self.font_heading = ("Helvetica", "12", "bold")
        self.font_setting = ("Helvetica", "11")


        self.afk = False # Controlled by afk start/stop button
        self.keys = None # Changed when key presses are recorded for afk playback, of type keyboard.KeyboardEvent
        self.app = ""
        
        # Frame to hold applist and related widgets
        self.frame_apps = Frame(self.root, padx=10, pady=10)
        self.frame_apps.grid(column=0, row=0, sticky=N)
        # Label for list of windows/apps
        Label(self.frame_apps, text="Windows", font=self.font_heading).grid(row=0, sticky=W)
        # Creating and populating listbox containing apps
        self.listbox_apps = Listbox(self.frame_apps, width=40, font=self.font_container) # Create listbox to allow user to select app
        self.updateAppsList()
        self.listbox_apps.grid(row=1, pady=5) # Place listbox in root window
        # Button to refresh apps/windows list
        Button(self.frame_apps, text="REFRESH LIST", command=self.updateAppsList, width=40).grid(row=2)
        
        # Frame to hold keypress related widgets
        self.frame_keypresses = Frame(self.root, padx=10, pady=10)
        self.frame_keypresses.grid(column=1, row=0, sticky=N)
        # Label for keypress set up/configuration
        Label(self.frame_keypresses, text="Set up keypresses", font=self.font_heading).grid(row=0, sticky=W)
        # Listbox to hold recorded keypresses
        self.listbox_keypresses = Listbox(self.frame_keypresses, width=40, height=11, font=self.font_container, state="disabled")
        self.listbox_keypresses.grid(row=1, column=0, pady=5, ipady=7)
        # Frame for keyboard recording buttons
        self.frame_keypresses_buttons = Frame(self.frame_keypresses)
        self.frame_keypresses_buttons.grid(row=1, column=1, pady=5, padx=5)
        # Buttons for keyboard recording related stuff, temprorary config for some
        Button(self.frame_keypresses_buttons, text="Record Keys", width=15, command=self.record).grid(row=0)
        Button(self.frame_keypresses_buttons, text="Clear Recording", width=15, command=self.clearKeys).grid(row=1, pady=20)
        Label(self.frame_keypresses_buttons, text="Delay:", font=self.font_setting).grid(row=2, sticky=W)
        self.textbox_playbackDelay = Entry(self.frame_keypresses_buttons, width=15, font=self.font_container)
        self.textbox_playbackDelay.grid(row=3)

    def start(self):
        self.root.mainloop()

    def updateAppsList(self):
        global app_exclusion

        self.listbox_apps.delete('0', 'end') # Clear list

        windows = [w.window_text() for w in Desktop(backend="uia").windows()] # active windows (static)
        # Loop through applications and insert at bottom of listbox
        for window in windows:
            if window not in app_exclusion and window != self.root.title():
                self.listbox_apps.insert(-1, window)

        # Scroll to top of list, forces update to listbox display
        self.listbox_apps.yview_moveto(0)

    def record(self):
        messagebox.showinfo( "Hello User", "Currently, recording hasn't been implemented")

    def clearKeys(self):
        messagebox.showinfo( "Hello User", "Currently, clearing recordings hasn't been implemented")

    def getForegroundWindow(self):
        hWnd = windll.user32.GetForegroundWindow()
        length = windll.user32.GetWindowTextLengthW(hWnd)
        buf = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hWnd, buf, length + 1)
        return buf.value if buf.value else "None"

# def pauseLoop():
#     global running
#     nowTime = datetime.now()
#     currTime = nowTime.strftime("%H:%M:%S")
#     paused = " # " + ("Paused" if running else "Unpaused")
#     print(currTime + paused)
#     running = False if running else True

# keyboard.add_hotkey('F2', closeLoop, suppress=True) # End app
# keyboard.add_hotkey('F3', pauseLoop, suppress=True) # Pause app

if __name__ == "__main__":
    app = Main()
    app.start()