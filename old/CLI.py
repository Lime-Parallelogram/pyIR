#---------------------------------------------------------------------#
#Name - IR&NECDataCollect.py
#Description - Reads data from the IR sensor but uses the official NEC Protocol (command line version)
#Author - Lime Parallelogram
#Licence - Attribution Lime
#Date - 06/07/19 - 18/08/19
#---------------------------------------------------------------------#
#Imports modules
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
	
#==================#
#Promps for values
#Input pin
while True:
	PinIn = raw_input("Please enter your sensor pin: ")
	try:
		PinIn = int(PinIn)
		break
	except:
		pass
#Remote name
remote = raw_input("Please enter a name for you remote: ")

#==================#
#Creates output file
output = open(remote+".txt", 'a')
output.writelines("Button codes regarding " + remote + " IR controller:")
output.close()

#==================#
#Sets up GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PinIn,GPIO.IN)

#==================#
#Defines Subs	
def ConvertHex(BinVal): #Converts binary data to hexidecimal
	tmpB2 = int(str(BinVal), 2)
	return hex(tmpB2)
		
def getData(): #Pulls data from sensor
	num1s = 0 #Number of consecutive 1s
	command = [] #Pulses and their timings
	binary = 1 #Decoded binary command
	previousValue = 0 #The previous pin state
	value = GPIO.input(PinIn) #Current pin state
	
	while value: #Waits until pin is pulled low
		value = GPIO.input(PinIn)
	
	startTime = datetime.now() #Sets start time
	
	while True:
		if value != previousValue: #Waits until change in state occurs
			now = datetime.now() #Records the current time
			pulseLength = now - startTime #Calculate time in between pulses
			startTime = now #Resets the start time
			command.append((previousValue, pulseLength.microseconds)) #Adds pulse time to array (previous val acts as an alternating 1 / 0 to show whether time is the on time or off time)
		
		#Interrupts code if an extended high period is detected (End Of Command)	
		if value:
			num1s += 1
		else:
			num1s = 0
		
		if num1s > 10000:
			break
		
		#Reads values again
		previousValue = value
		value = GPIO.input(PinIn)
		
	#Covers data to binary
	for (typ, tme) in command:
		if typ == 1:
			if tme > 1000: #According to NEC protocol a gap of 1687.5 microseconds repesents a logical 1 so over 1000 should make a big enough distinction
				binary = binary * 10 + 1
			else:
				binary *= 10
				
	if len(str(binary)) > 34: #Sometimes the binary has two rouge charactes on the end
		binary = int(str(binary)[:34])
		
	return binary
	
def runTest(): #Actually runs the test
	#Takes samples
	command = ConvertHex(getData())
	print("Hex value: " + str(command)) #Shows results on the screen
	return command
	###

#==================#
#Main program loop
while True:
  if raw_input("Press enter to start. Type q to quit. ") == 'q':
    break
  finalData = runTest()
  if raw_input("Save? y/n.") == 'y':
    name = raw_input("Enter a name for your button: ")
    output = open(remote+".txt", 'a')
    output.writelines("""
Button Code - """ + name + ": " + str(finalData))
    output.close()
GPIO.cleanup()
