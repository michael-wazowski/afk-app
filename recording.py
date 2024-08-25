from tkinter import *
from time import time
import keyboard

class Recording:
    def __init__(self, output: Listbox=None):
        self.output_box = output

        print(type(self._disableEvent))

        self.record_window = Toplevel()
        self.record_window.resizable(False, False)
        self.record_window.protocol("WM_DELETE_WINDOW", self._disableEvent)

        # Label to inform user that keyboard is being recorded
        Label(self.record_window, text="You are currently recording your keyboard for playback.\nClick the button below to stop.").grid(sticky=N+E+S+W, pady=10, padx=10)

        # Place button to stop recording keypresses here
        Button(self.record_window, text="Stop Recording", command=self._stopRecording).grid(sticky=N+E+S+W, pady=10, padx=10)
        
        # start recording
        self.recording = keyboard.start_recording()
        # set start_time here for delta calculations for ui
        self.start_time = time()
    
    # Disables close window button
    def _disableEvent(self):
        pass

    def _stopRecording(self, zero=0):
        # Sanity check, in case method is triggered outside normal parameters
        if self.recording != None:
            self.recording = keyboard.stop_recording()

            # If start from recording 0s is off
            if zero == 0 and len(self.recording) > 0:
                self.start_time = self.recording[0].time # Get start time of first keypress

            if self.output_box != None:
                self.output_box.config(state=NORMAL)

                for keyEvent in self.recording:
                    self.output_box.insert(END, keyEvent.name+"_"+ keyEvent.event_type + " : %0.3f" % (keyEvent.time-self.start_time))

                self.output_box.yview_moveto(0)
                self.output_box.config(state=DISABLED)
    
            self.record_window.destroy() # Close window for recording keys
    
    # Return recorded keys list
    def getRecording(self):
        return self.recording