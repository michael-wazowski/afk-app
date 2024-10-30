from tkinter import *
from time import time
import keyboard

class Recording:
    def __init__(self, output: Listbox=None, load_info:dict=None):
        self.output_box = output

        # If not loading from file
        if not load_info:
            # Record like normal
            self._startRecording()
        else:
            # Run load method passing acquired data
            self._loadKeys(load_info['keys'])
    
    # Disables close window button
    def _disableEvent(self):
        pass
    
    def _startRecording(self):
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

    def _stopRecording(self, zero=0):
        # Sanity check, in case method is triggered outside normal parameters
        if self.recording != None:
            self.recording = keyboard.stop_recording()

            # Remove duplicate key entries due to holding down key
            # COME BACK TO THIS EVENTUALLY - IT IS IMPORTANT
            # ptr = 0
            # skipInfo = {}
            # while ptr < len(self.recording):
            #     curr = self.recording[ptr]
            #     next = self.recording[ptr+1]
            #     if curr.name == next.name and curr.event_type == next.event_type:
            #         if next.time-curr.time <= 0.05:
            #             skipInfo[str(ptr)] = ptr+1
            #     ptr += 1

            # If start from recording 0s is off
            if zero == 0 and len(self.recording) > 0:
                self.start_time = self.recording[0].time # Get start time of first keypress

            if self.output_box != None:
                self.output_box.config(state=NORMAL)

                for keyEvent in self.recording:
                    self.output_box.insert(END, keyEvent.name+"_"+ keyEvent.event_type + " : %0.3f" % (keyEvent.time-self.start_time))
                    keyEvent.time = round(keyEvent.time-self.start_time, 3)

                self.output_box.yview_moveto(0)
                self.output_box.config(state=DISABLED)
    
            self.record_window.destroy() # Close window for recording keys
    
    # Core method for loading key "recording" from file
    def _loadKeys(self, keys:list): 
        output = [] # temp list for processing
        total_time = 0.0 # Total time so far in recording
        self.start_time = 0

        # Loop through each item and get the key to be controlled
        for key in keys:
            key_name = list(key.keys())[0]
            # If there is no delta, don't bother processing key
            if "delta" in key[key_name]:
                # Get scan code and delta time, and sum total time
                key_code = keyboard.key_to_scan_codes(key_name)[0]
                key_delta = float(key[key_name]["delta"])
                total_time = float(total_time+key_delta)
                # If a event type is specified, set key_type
                if "type" in key[key_name]:
                    key_type = key[key_name]["type"]
                    if key[key_name]["type"] == "press": # If key type was press, then immediately create a down press of key_name
                        output.append(keyboard.KeyboardEvent(event_type="down", scan_code=key_code, time=total_time, name=key_name))
                        # And change the settings accordingly for a key up of key_name
                        key_type = "up"
                        key_delta = 0.1
                        total_time = float(total_time+key_delta)
                # No type specified, so do the same as was done for press
                elif "type" not in key[key_name]:
                    output.append(keyboard.KeyboardEvent(event_type="down", scan_code=key_code, time=total_time, name=key_name))
                    key_type = "up"
                    key_delta = 0.1
                    total_time = float(total_time+key_delta)
                
                # Default key event creation, runs for all valid keys
                output.append(keyboard.KeyboardEvent(event_type=key_type, scan_code=key_code, time=total_time, name=key_name))
        
        # Set output to proper internal variable 
        self.recording = output
        # Output to provided listbox
        if self.output_box != None:
                self.output_box.config(state=NORMAL)

                for keyEvent in self.recording:
                    self.output_box.insert(END, keyEvent.name+"_"+ keyEvent.event_type + " : %0.3f" % (keyEvent.time))
                    keyEvent.time = round(keyEvent.time-self.start_time, 3)

                self.output_box.yview_moveto(0)
                self.output_box.config(state=DISABLED)

    
    # INTENDED TO NORMALISE EVENTS AND PREVENT OVERLAP FROM TYPING
    # e.g. a_down -> b_down -> a_up -> b_up  and similar situations
    # def normaliseKeys(self, spec_chars:list=["ctrl", "shift", "alt"]):
    #     self.recNormal = self.recording
    
    # Return recorded keys list
    def getRecording(self):
        return self.recording

    def outputKeys(self):
        keys = []

        kp = 0
        delta = 0
        while kp < len(self.recording):
            curr = self.recording[kp]
            next = self.recording[kp+1] if kp < len(self.recording)-1 else self.recording[kp]
            if curr.name == next.name and curr.event_type != next.event_type:
                if round(next.time-curr.time, 5) <= 0.1:
                    keys.append({
                        str(curr.name) : {
                        "type":"press",
                        "delta": round(curr.time-delta, 3)
                        }
                    })
                    delta = next.time
                    kp += 1
                else:
                    keys.append({
                        str(curr.name) : {
                        "type": curr.event_type,
                        "delta": round(curr.time-delta, 3)
                        }
                    })
                    delta = curr.time
            else:
                keys.append({
                    str(curr.name) : {
                    "type": curr.event_type,
                    "delta": round(curr.time-delta, 3)
                    }
                })
                delta = curr.time
        
            kp += 1
        
        return keys

    

    # Process recording for paused playback at any key
    # DOES NOT TAKE KEYS LIKE SHIFT AND CTRL INTO ACCOUNT
    # def processRecording(self, exclusions:list=[]):
    #     output = []
    #     process = {}

    #     for i in self.recording:
    #         if i.name in process.keys():
    #             if i.event_type == "up":
    #                 keys_t = list(process.keys())
    #                 items_t = list(process.values())

    #                 focal = keys_t.index(i.name)
    #                 items_t[focal:]
                    
    #                 output.append([process[i.name], i])
                    
    #                 del process[i.name]
    #         elif i.event_type == "down":
    #             process[i.name] = i

    #     return output