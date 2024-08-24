import keyboard
from time import sleep
from time import time
from ctypes import windll, create_unicode_buffer
from datetime import datetime
from pywinauto import Desktop
from tkinter import *
from tkinter import messagebox
# import yaml

# VARIABLE NAMING SCHEME:
# tkinterType_varPurpose
# e.g. frame_recording

# If, for example, frame in frame, then scheme is:
# tkinterType_parent_varPurpose
# e.g. frame_recording_buttons
# putting in any number of parent widget before varPurpose

app_exclusion = ["", "Taskbar", "Program Manager"] # "apps" to be excluded from apps/windows list

class Main:
    def __init__(self):
        # Initialising and setting up root window
        self.root = Tk()
        self.root.geometry("735x600")
        self.root.resizable(False, False)
        self.root.title("AFK App")
        self.root.rowconfigure(1, weight=1)

        # Font styles
        self.font_container = ("Times New Roman", "11")
        self.font_heading = ("Helvetica", "12", "bold")
        self.font_setting = ("Helvetica", "11")

        # Internal functionality variables
        self.afk = False # Controlled by afk start/stop button
        self.keys = None # Changed when key presses are recorded for afk playback, of type keyboard.KeyboardEvent
        self.app = ""
        self.var_trueZero = IntVar() # Determines whether to include wait time between start recording actual keypresses
        self.start_time = None 
        
        # Frame to hold applist and related widgets
        self.frame_apps = Frame(self.root, padx=10, pady=10)
        self.frame_apps.grid(column=0, row=0, sticky=N+E+S+W)
        # Label for list of windows/apps
        Label(self.frame_apps, text="Windows", font=self.font_heading).grid(row=0, sticky=W)
        # Creating and populating listbox containing apps
        self.listbox_apps = Listbox(self.frame_apps, width=40, font=self.font_container) # Create listbox to allow user to select app
        self.updateAppsList()
        self.listbox_apps.grid(row=1, pady=5) # Place listbox in root window
        # Button to refresh apps/windows list
        Button(self.frame_apps, text="REFRESH LIST", command=self.updateAppsList, width=40).grid(row=2)
        
        # Frame to hold keypress related widgets
        self.frame_recording = Frame(self.root, padx=10, pady=10)
        self.frame_recording.grid(column=1, row=0, sticky=N+E+W+S)
        # Label for keypress set up/configuration
        Label(self.frame_recording, text="Set up keypresses", font=self.font_heading).grid(row=0, sticky=W)
        # Listbox to hold recorded keypresses
        self.listbox_recording = Listbox(self.frame_recording, width=40, height=11, font=self.font_container, state=DISABLED, disabledforeground="black")
        self.listbox_recording.grid(row=1, column=0, pady=5, ipady=7)
        # Frame for keyboard recording buttons
        self.frame_recording_buttons = Frame(self.frame_recording)
        self.frame_recording_buttons.grid(row=1, column=1, pady=5, padx=5)
        # Buttons for keyboard recording related stuff
        Button(self.frame_recording_buttons, text="Record Keys", width=15, command=self.record).grid(row=0)
        Button(self.frame_recording_buttons, text="Clear Recording", width=15, command=self.clearKeys).grid(row=1, pady=20)
        # Checkbox for true zero in ui (not functional, may never be)
        self.checkbtn_zeroTime = Checkbutton(self.frame_recording_buttons, variable=self.var_trueZero, onvalue=1, offvalue=0)
        self.checkbtn_zeroTime.grid(row=4)

        # Frame for start/stop of playback, and log of start/stop
        self.frame_playback_logger = Frame(self.root, padx=10, pady=10,  highlightbackground="black", highlightthickness=1)
        self.frame_playback_logger.grid(column=0, columnspan=2, row=1, sticky=N+E+W+S)
        self.frame_playback_logger.rowconfigure(1, weight=1)

        # Inner frame for playback controls/settings
        self.frame_playback_logger_settings = Frame(self.frame_playback_logger, highlightbackground="black", highlightthickness=1)
        self.frame_playback_logger_settings.grid(row=0, column=0, sticky=N+E+W)

        # Label for delay
        Label(self.frame_playback_logger_settings, text="Playback Delay:", font=self.font_setting).grid(row=0, column=0)
        # String variable to contain defaults and input from user for playback delay
        self.var_playbackDelay = StringVar(value="0")
        # Single-line textbox to get playback delay from user
        self.textbox_playbackDelay = Entry(self.frame_playback_logger_settings, width=15, font=self.font_container, textvariable=self.var_playbackDelay, justify="center")
        self.textbox_playbackDelay.grid(row=1, column=0)
        
        # Listbox to log playback activity
        self.listbox_logger = Listbox(self.frame_playback_logger, font=self.font_container, state=DISABLED, disabledforeground="black", width=101)
        self.listbox_logger.grid(column=0, row=1, sticky=E+W+S)

    # Method to start the application
    def start(self):
        self.root.mainloop()

    # Update the listbox containing open applications
    def updateAppsList(self):
        global app_exclusion

        self.listbox_apps.delete('0', END) # Clear list

        windows = [w.window_text() for w in Desktop(backend="uia").windows()] # active windows (static)
        # Loop through applications and insert at bottom of listbox
        for window in windows:
            if window not in app_exclusion and window != self.root.title():
                self.listbox_apps.insert(END, window)

        # Scroll to top of list, forces update to listbox display
        self.listbox_apps.yview_moveto(0)

    # Record keypresses until end signal and process
    def record(self):
        self.record_window = Toplevel()
        self.record_window.resizable(False, False)
        self.record_window.protocol("WM_DELETE_WINDOW", self._disableEvent)

        # Label to inform user that keyboard is being recorded
        Label(self.record_window, text="You are currently recording your keyboard for playback.\nClick the button below to stop.").grid(sticky=N+E+S+W, pady=10, padx=10)

        # Place button to stop recording keypresses here
        Button(self.record_window, text="Stop Recording", command=self._stopRecording).grid(sticky=N+E+S+W, pady=10, padx=10)
        
        # start recording
        self.keys = keyboard.start_recording()
        # set start_time here for delta calculations for ui
        self.start_time = time()
    
    # internal method to stop recording keypresses
    def _stopRecording(self):
        # Sanity check, in case method is triggered outside normal parameters
        if self.keys != None:
            self.keys = keyboard.stop_recording()

            # If start from recording 0s is off
            if self.var_trueZero.get() == 0:
                self.start_time = self.keys[0].time # Get start time of first keypress

            self.listbox_recording.config(state=NORMAL)

            for keyEvent in self.keys:
                self.listbox_recording.insert(END, keyEvent.name+"_"+ keyEvent.event_type + " : " + str(keyEvent.time-self.start_time))

            self.listbox_recording.yview_moveto(0)
            self.listbox_recording.config(state=DISABLED)
    
            self.record_window.destroy() # Close window for recording keys

    # Clear recorded keypresses and relevant widgets
    def clearKeys(self):
        self.listbox_recording.config(state=NORMAL)
        self.listbox_recording.delete('0', END)
        self.listbox_recording.yview_moveto(0)
        self.listbox_recording.config(state=DISABLED)
        self.keys = None
    
    # Disables close window button
    def _disableEvent(self):
        pass

    # Get the active window, intended to use to auto-pause afk when not on selected application
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

# keyboard.add_hotkey('F3', pauseLoop, suppress=True) # Pause app

if __name__ == "__main__":
    app = Main()
    app.start()