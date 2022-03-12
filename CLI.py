#---------------------------------------------------------------------#
# File: /home/will/OneDrive/PiSpace/ByProject/Old YouTube Fix-Up/IR Code Decoder/IR-Code-Decoder--/CLI.py
# Project: /home/will/OneDrive/PiSpace/ByProject/Old YouTube Fix-Up/IR Code Decoder/IR-Code-Decoder--
# Created Date: Saturday, July 6th 2019, 8:54:52 pm
# Description: Reads data from an IR Sensor
# Author: Will Hall
# Copyright (c) 2022 Lime Parallelogram
# -----
# Last Modified: Sat Mar 12 2022
# Modified By: Will Hall
# -----
# HISTORY:
# Date          By    Comments
# ----------    ---    ---------------------------------------------------------
# 2022-03-08    WH    Loaded original file for editing
#---------------------------------------------------------------------#
#Imports modules
import time
import pyIR
from colorama import Fore

# ----------------- #
# Program constants
VALID_PINS = [1,3,5,7,8,10,11,12,13,15,16,18,19,21,22,23,24,26,29,31,32,33,35,36,37,38,40]

# ========================================= #
# Program Subroutines
# ----------------- #
# Present the main list of options to the user
def presentMainMenu():
    print()
    print("Chose an option to manage remotes: ")
    print("        N : Create new remote object")
    print("        L : Load remote from file")
    print("        V : View remote information")
    print("        A : Add buttons to remote")
    print("        S : Save remote to file")
    print("        T : Test button configuration by listening")
    print("        Q : Quit application")

    return input("Enter option : ").upper()

# ----------------- #
# Menu used to add buttons to a remote
def buttonAdd(sensor,remote):
    print("Welcome to button recording mode.")
    print("Once you enter all of the buttons you want to add, you will be prompted to press all of the buttons.")

    buttonNames = []
    while True:
        name = input("Enter the name of a button to add [leave blank when complete]: ")

        if name == "":
            break
    
        buttonNames.append(name)

    for button in buttonNames:
        print(f"Press button {button} now.")
        remote.recordButton(sensor,button)
        time.sleep(1)

# ----------------- #
# Check if a remote is open for editing and warn if not
def remoteLoaded(remote):
    if type(remote) == pyIR.Remote:
        return True

    print(Fore.RED+"No remote object is open for editing. Create or load a remote to perform this function!"+Fore.RESET)
    return False

# ========================================= #
# Create a sensor object
PinIn = input("Please enter your sensor pin: ")

while not PinIn in map(str,VALID_PINS):
    PinIn = input("INVALID PIN ENTERED! Please enter your sensor pin: ")

mySensor = pyIR.Receiver(int(PinIn))

# ----------------- #
# Main program execution
print("# ======================================================= #")
print("     Welcome to pyIR remote management utility.")
print(Fore.GREEN+"        Revision 2.0 - By Lime Parallelogram"+Fore.RESET)
print("# ======================================================= #")
myRemote = ""

while True:
    choice = presentMainMenu()

    if choice == "L": # Load remote from save
        try:
            filename = input("Filename to load: ")
            myRemote = pyIR.loadRemote(filename)
        except FileNotFoundError:
            print(Fore.RED+"The requested file could not be loaded."+Fore.RESET)

    elif choice == "N": # Create a new remote
        remoteName = input("Please enter a name for you remote: ")
        myRemote = pyIR.Remote(remoteName,pyIR.NEC)

        # Conveniently add buttons at the same time
        if input("Would you like to add buttons now? [y/N] ").upper() == "Y":
            buttonAdd(mySensor,myRemote)

    elif choice == "V": # Display a representation of the current remote
        if remoteLoaded(myRemote):
            myRemote.displayButtons()

    elif choice == "A": # Add buttons to remote
        if remoteLoaded(myRemote):
            buttonAdd(mySensor,myRemote)
    
    elif choice == "S": # Save remote information to file
        if remoteLoaded(myRemote):
            filename = input("Filename to write: ")
            myRemote.saveRemote(filename)
    
    elif choice == "T": # Test the button configuration by listening
        if remoteLoaded(myRemote):
            button = mySensor.listen(remotes=[myRemote])
            print(f"The button '{button.getNickname()}' was pressed.")

    elif choice == "Q":
        break