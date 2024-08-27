import keyboard
from time import sleep, time
from ctypes import windll, create_unicode_buffer
from datetime import datetime
from pywinauto import Desktop
from tkinter import *
from tkinter import messagebox
from threading import Thread

import yaml.loader
from recording import Recording
from tkinter.filedialog import askopenfilename, asksaveasfilename
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

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
        self.unpaused = True
        self.keys = None # Changed when key presses are recorded for afk playback, of type keyboard.KeyboardEvent
        self.app = ""
        self.var_trueZero = IntVar() # Determines whether to include wait time between start recording actual keypresses
        self.start_time = None
        self.playbackThread = None

        # root register function to validate spinbox input
        self._rValidateSpinBox = (self.root.register(self._validateSpinBox), '%P')
        
        # Functions to load certain sets of widgets
        # Loads app list and refresh button
        self._loadAppsWidgets()
        # Load recording listbox and related buttons
        self._loadRecordingWidgets()
        # Loads logger and playback configs and buttons
        self._loadPlaybackLoggerWidgets()

    # Method to start the application
    def start(self):
        self.root.mainloop()

    def _loadAppsWidgets(self):
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
    
    def _loadRecordingWidgets(self):
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
        Button(self.frame_recording_buttons, text="Save Recording", width=15, command=self.save).grid(row=0, pady=10)
        Button(self.frame_recording_buttons, text="Load Recording", width=15, command=self.load).grid(row=1, pady=10)
        Button(self.frame_recording_buttons, text="Record Keys", width=15, command=self.record).grid(row=2, pady=10)
        Button(self.frame_recording_buttons, text="Clear Recording", width=15, command=self.clearKeys).grid(row=3, pady=10)
        # Checkbox for true zero in ui (not functional, may never be)
        # self.checkbtn_zeroTime = Checkbutton(self.frame_recording_buttons, variable=self.var_trueZero, onvalue=1, offvalue=0)
        # self.checkbtn_zeroTime.grid(row=4)
    
    def _loadPlaybackLoggerWidgets(self):
        # Frame for start/stop of playback, and log of start/stop
        self.frame_playbackLogger = Frame(self.root,  highlightbackground="black", highlightthickness=1)
        self.frame_playbackLogger.grid(column=0, columnspan=2, row=1, sticky=N+E+W+S)
        self.frame_playbackLogger.rowconfigure(1, weight=1)

        # Title label
        Label(self.frame_playbackLogger, text="Configure and Playback Keypresses", font=self.font_heading).grid(row=0, column=0, sticky=W+N, padx=5)

        # Further separated cos there was so much
        # Loads widgets for playback settings and buttons
        self._loadPlaybackControlsSettings()

        # Listbox to log playback activity
        self.listbox_logger = Listbox(self.frame_playbackLogger, font=self.font_container, state=DISABLED, disabledforeground="black", width=101)
        self.listbox_logger.grid(column=0, row=2, sticky=E+W+S, padx=10, pady=10)
    
    def _loadPlaybackControlsSettings(self):
        # Inner frame for playback controls/settings
        self.frame_playbackLogger_settings = Frame(self.frame_playbackLogger, highlightbackground="black", highlightthickness=1)
        self.frame_playbackLogger_settings.grid(row=1, column=0, sticky=N+E+W, padx=5, pady=10)

        # Delay at start of playback - default is 0
        Label(self.frame_playbackLogger_settings, text="Playback Delay:", font=self.font_setting).grid(row=0, column=0, padx=5)
        self.var_playbackDelay = StringVar(value="3") # Delay amount in seconds
        self.textbox_playbackDelay = Spinbox(self.frame_playbackLogger_settings, width=15, font=self.font_container, textvariable=self.var_playbackDelay, justify=CENTER, to=1000, validate=ALL, validatecommand=self._rValidateSpinBox)
        self.textbox_playbackDelay.grid(row=1, column=0, padx=5)

        # To loop playback setting
        Label(self.frame_playbackLogger_settings, text="Loop Playback:", font=self.font_setting).grid(row=0, column=1, padx=5)
        self.var_playbackLoop = IntVar(value=1)
        self.checkbtn_playbackLoop = Checkbutton(self.frame_playbackLogger_settings, variable=self.var_playbackLoop, onvalue=1, offvalue=0)
        self.checkbtn_playbackLoop.grid(row=1, column=1, sticky=E+W, padx=5)

        # Number of times to loop - default is 0 which means until the user stops or conditions are met
        Label(self.frame_playbackLogger_settings, text="Loop Limit:", font=self.font_setting).grid(row=0, column=2, padx=5)
        self.var_loopLimit = StringVar(value="0") # Delay amount in seconds
        self.textbox_loopLimit = Spinbox(self.frame_playbackLogger_settings, width=15, font=self.font_container, textvariable=self.var_loopLimit, justify=CENTER, to=1000, validate=ALL, validatecommand=self._rValidateSpinBox)
        self.textbox_loopLimit.grid(row=1, column=2, padx=5)

        # Button to start/stop playback
        Button(self.frame_playbackLogger_settings, text="Start/Stop Playback", command=self.playbackRecording, font=self.font_setting).grid(row=0, rowspan=2, column=3, padx=5, sticky=E)
        # Button to pause/unpause playback
        Button(self.frame_playbackLogger_settings, text="Pause/Unpause Playback", command=self.pausePlayback, font=self.font_setting).grid(row=0, rowspan=2, column=4, padx=5, sticky=E)

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
    
    def _validateSpinBox(self, text):
        return text.isnumeric() or text==''

    # Record keypresses until end signal and process
    def record(self):
        self.keys = Recording(self.listbox_recording)

    # Clear recorded keypresses and relevant widgets
    def clearKeys(self):
        self.listbox_recording.config(state=NORMAL)
        self.listbox_recording.delete('0', END)
        self.listbox_recording.yview_moveto(0)
        self.listbox_recording.config(state=DISABLED)
        self.keys = None

    # Get the active window, intended to use to auto-pause afk when not on selected application
    def getForegroundWindow(self):
        hWnd = windll.user32.GetForegroundWindow()
        length = windll.user32.GetWindowTextLengthW(hWnd)
        buf = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hWnd, buf, length + 1)
        return buf.value if buf.value else "None"

    # Func to loop x number of times for playback
    def _playbackLoop(self, loopLimit, playbackDelay):
        self._sendToLogger("Starting playback")
        # While user is afk and loop count is in ranges
        while (loopLimit > 0 or loopLimit < 0) and self.afk:
            # If playback not pause by user
            if self.unpaused:
                if playbackDelay > 0:
                    sleep(playbackDelay)
                keyboard.play(self.keys.getRecording())
                # for key in self.keys.processRecording():
                #     keyboard.play(key)
                loopLimit -= 1
            else:
                sleep(1)

        self.afk = False
        self._sendToLogger("Playback stopped")

    def _sendToLogger(self, logMessage):
        # Construct full message to send to logger
        currentTime = (datetime.now()).strftime("%H:%M:%S")
        msg = currentTime + " # " + logMessage
        # Unlock logger and "write" message before forcing update
        self.listbox_logger.config(state=NORMAL)
        self.listbox_logger.insert(END, msg)
        self.listbox_logger.config(state=DISABLED)
        self.listbox_logger.yview_scroll(1, UNITS)

    # Actually starts/stops playback of recorded keypresses
    def playbackRecording(self):
        # If there might be a recording, AND it is a recording (they are a list) and there are actual keypresses in there
        if self.keys != None and type(self.keys.getRecording()) == type([]) and len(self.keys.getRecording()) > 0:
            # If currently playing back recording
            if self.playbackThread != None and self.afk:
                self._sendToLogger("Stopping playback...")
                self.afk = False

                # Wait until playback thread is done
                while self.playbackThread.is_alive():
                    pass
                self.playbackThread = None # reset var
                return # End func call early
            
            # Get user config values and process them
            playbackDelay = int(self.var_playbackDelay.get())
            looping = self.var_playbackLoop.get()==1
            # If user wants to loop playback
            if looping:
                loopLimit = self.var_loopLimit.get()
                if int(loopLimit) > 0:
                    loopLimit = int(loopLimit)
                else:
                    loopLimit = -1
            else:
                # Since it only runs once anyways, just fix loops to 1
                loopLimit = 1
            
            # Set afk to true show that looped playback is occurring 
            self.afk = True
            # Init and start playback
            self.playbackThread = Thread(target=self._playbackLoop, args=[loopLimit, playbackDelay])
            self.playbackThread.start()
    
    # Function to pause playback
    def pausePlayback(self):
        # Log according to current pause state
        if self.unpaused:
            self._sendToLogger("Pausing playback")
        else:
            self._sendToLogger("Unpausing playback")
        # Alternate pause state using python ternary equivalent
        self.unpaused = False if self.unpaused else True
    
    # Core method to save recording and config
    def save(self):
        pass

    # Core method to load recording and config
    def load(self):
        # Get filepath from user and load yaml file
        filepath = askopenfilename(filetypes=[("YAML Files", "*.yaml")])
        with open(filepath, 'rt', encoding='utf8') as recFile:
            data = yaml.load(recFile, Loader=Loader)
        
        # Branch according to what is in the file
        if "config" in data:
            self._loadConfig(data["config"])
        if "keys" in data:
            self.keys = Recording(self.listbox_recording, True, data["keys"])

    # Set the information depending on what is found
    def _loadConfig(self, config:dict):
        if "delay" in config:
            self.var_playbackDelay.set(str(config["delay"]))
        # Loop was auto-converted to py bool
        if "loop" in config:
            if config["loop"]:
                self.var_playbackLoop.set(1) # yes loop
            elif config["loop"] == False:
                self.var_playbackLoop.set(0) # no loop
        if "loop_limit" in config:
            self.var_loopLimit.set(str(config["loop_limit"]))

# keyboard.add_hotkey('F3', pauseLoop, suppress=True) # Pause app

if __name__ == "__main__":
    app = Main()
    app.start()