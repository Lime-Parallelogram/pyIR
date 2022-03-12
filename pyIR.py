#---------------------------------------------------------------------#
# File: https://github.com/Lime-Parallelogram/pyIR/pyIR.py
# Project: https://github.com/Lime-Parallelogram/pyIR
# Created Date: Monday, March 7th 2022, 9:15:49 pm
# Description: A new Object-Oriented approach to an IR Code receiver module
# Author: Will Hall
# -----
# Last Modified: Sat Mar 12 2022
# Modified By: Will Hall
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	---------------------------------------------------------
# 2022-03-11	WH	Added listen option to identify incoming commands
# 2022-03-10	WH	Moved remote load outside of remote class and added functionality to load nickname and protocol properties.
# 2022-03-09	WH	Added load and save function to system
# 2022-03-07	WH	Added class for NEC protocol and added translation code inside it
# 2022-03-07	WH	Added Receiver, Remote and button class
#---------------------------------------------------------------------#
# Imports Modules
from time import sleep
import RPi.GPIO as GPIO
from datetime import datetime

#Setup GPIO connection
GPIO.setmode(GPIO.BOARD)

# Create a hardware sensor class
class Receiver:
    """Create a hardware sensor object."""

    def __init__(self,pin):
        self.sensorPin = pin # Note: this program uses the GPIO.BOARD numbering scheme
        GPIO.setup(self.sensorPin,GPIO.IN)
        self.remotes = []

    # ----------------- #
    # Add a remote object to this receiver
    def addRemote(self,remote):
        self.remotes.append(remote)
    
    # ----------------- #
    # Wait for data to be received then return it
    def getRAW(self):
        num1s = 0 # Number of consecutive 1s
        command = [] # Pulses and their timings
        previousValue = 0 # The previous pin state

        value = GPIO.input(self.sensorPin) # Current pin state
        
        while value: # Waits until pin is pulled low
            sleep(0.0001)
            value = GPIO.input(self.sensorPin)
        
        startTime = datetime.now() # Sets start time
        
        while num1s < 10000:
            if value != previousValue: # Waits until change in state occurs
                now = datetime.now() # Records the current time
                pulseLength = now - startTime # Calculate time in between pulses
                startTime = now # Resets the start time
                command.append((previousValue, pulseLength.microseconds)) # Adds pulse time to array (previous val acts as an alternating 1 / 0 to show whether time is the on time or off time)
            
            # Interrupts code if an extended high period is detected (End Of Command)	
            if value:
                num1s += 1
            else:
                num1s = 0
            
            # Reads values again
            previousValue = value
            value = GPIO.input(self.sensorPin)
        
        return command # Returns the raw information about the high and low pulses (HIGH/LOW, time µs)

    # ----------------- #
    # Listen for incoming data and identify button
    def listen(self,remotes=[]):
        if remotes == []:
            remotes = self.remotes

        while True:
            raw = self.getRAW()
            for remote in remotes:
                match = remote.identifyButton(remote.getBinary(raw))
                if match != -1:
                    return match

# ========================================= #
#^ Information for functions relating to the NEC IR Protocol ^#
class NEC:
    # ----------------- #
    # Take the data about the times of pulses and convert to a binary data string according to NEC protocol
    def getBinary(self,rawDATA):
        binary = 1 # Decoded binary command
        
        # Covers data to binary
        for (typ, tme) in rawDATA:
            if typ == 1: # Ignore the LOW periods, these should be consitant and thus irrelevant
                if tme > 1000: # According to NEC protocol a gap of 1687.5 microseconds represents a logical 1 so over 1000 should make a big enough distinction
                    binary = binary * 10 + 1
                else:
                    binary *= 10
                    
        if len(str(binary)) > 34: # Sometimes the binary has two rouge characters on the end
            binary = int(str(binary)[:34])
        
        return binary
    
    def getClassName(self):
        return "NEC"

# ========================================= #
#^ Remote control objects ^#
class Remote:
    """All functions related to a remote are stored here"""

    def __init__(self,name,protocol):
        self.nickname = name
        self.buttons = []
        self.protcol = protocol()
    
    # Return the binary value from raw data using the remote's protocol's method
    def getBinary(self, raw):
        return self.protcol.getBinary(raw)

    # Reccord a new button using sensor capture
    def recordButton(self,sensor : Receiver, buttonNickname):
        print("Ready to record data. Press the button on your remote! ")
        rawData = sensor.getRAW()
        binary = self.getBinary(rawData)
        self.buttons.append(Button(buttonNickname,binary))

    # Pint out a table that shows all of the buttons in the current remote
    def displayButtons(self):
        NICKNAME_CELL_LENGTH = 15
        HEX_CELL_LENGTH = 20
        ROW_SEPARATOR = "+-" + "-"*NICKNAME_CELL_LENGTH + "-+-" + "-"*HEX_CELL_LENGTH +"-+"

        print(ROW_SEPARATOR)
        print("| Nickname        | Hex Code             |")
        print(ROW_SEPARATOR)
        for button in self.buttons:
            print("| " + button.getNickname() + (NICKNAME_CELL_LENGTH-len(button.getNickname()))*" " + " | " + button.getHex() + (HEX_CELL_LENGTH-len(button.getHex()))*" "+" |")
            print(ROW_SEPARATOR)
    
    # Save remote data to a file
    def saveRemote(self,filename):
        with open(filename,'w') as file:
            # Save properties of the class
            file.writelines("nickname:"+self.nickname+"\n")
            file.writelines("protocol:"+self.protcol.getClassName()+"\n")

            # Save buttons to file separated by '|'
            file.writelines("buttons:")
            for button in self.buttons:
                file.writelines(button.getData()+"|")
    
    # Add a button with given name and binary
    def addButton(self,name,binary):
        self.buttons.append(Button(name,binary))

    # Return button object based on given binary value
    def identifyButton(self,binary):
        for button in self.buttons:
            if button.getBinary() == str(binary):
                return button

        return -1
    
# ========================================= #
#^ Class for each button ^#
class Button:
    """An individual button object"""

    def __init__(self,name,binary):
        self.nickname = name
        self.binary = binary

    # ----------------- #
    # Simple getter and setter methods #
    def getNickname(self):
        return self.nickname
    
    def getBinary(self):
        return self.binary
    
    def getHex(self):
        tmpB2 = int(str(self.binary), 2)
        return hex(tmpB2)
    
    def getData(self): # Get data in format that can be written to data file
        return ",".join([self.nickname,str(self.binary)])

# ========================================= #
#^ Create a remote object from an information file ^#
# Load remote data from file into object
def loadRemote(filename):
    # Open file and read data
    with open(filename) as file:
        data = file.readlines()

    # Load all properties from file into dictionary
    remoteInfo = {}
    for line in data:
        propertyName, dataValue = line.split(":")
        remoteInfo[propertyName] = dataValue

    try:
        newRemote = Remote(remoteInfo["nickname"],eval(remoteInfo["protocol"])) # Create remote object from dictionary

        # Handle all buttons that were specified in the save
        for button in remoteInfo["buttons"].split("|"): # Different buttons separated by '|'
            if button != "":
                buttonDat = button.split(",") # Button information separated by commas
                newRemote.addButton(buttonDat[0],buttonDat[1])
        
        return newRemote

    except KeyError:
        print("File Invalid! Not all properties present.")
    
    