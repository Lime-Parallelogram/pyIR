#---------------------------------------------------------------------#
#Name - IR&NECDataCollect.py
#Description - Reads data from the IR sensor but uses the official NEC Protocol
#Author - Will Hall
#Licence - Attribution Lime
#Date - 06/07/19
#---------------------------------------------------------------------#
#Imports modules
import RPi.GPIO as GPIO
import pygame
import pygame.display
from time import sleep
from datetime import datetime

#==================#
#Sets up Pygame
pygame.init()
pygame.display.init()

#==================#
class TextEntry:
	global prompt
	global UI
	def showPrompt(self, starttext):
		global prompt
		size = (400, 120)
		#---------#
		keyIcon = pygame.image.load("res/keyboard-icon.png")
		pygame.display.set_caption("Input Prompt")
		pygame.display.set_icon(keyIcon)
		prompt = pygame.display.set_mode(size)
		prompt.fill((255,255,255))
		
		#---------#
		FontDATA = pygame.font.SysFont("Arial", 20)
		textRENDER = FontDATA.render(starttext, True, (191,181,171))
		prompt.blit(textRENDER, (5,5))
		pygame.display.update()
		###
		
	def getInput(self):
		global prompt
		FontDATA = pygame.font.SysFont("Arial", 15)
		word = ""
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					import sys
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						return word
						pygame.draw.rect(UI, (255,255,255) (0,0,0,0), 0)
						pygame.display.update()
						break
					elif event.key == pygame.K_BACKSPACE:
						word = word[:len(word)-1]
					else:
						try:
							word = word + chr(event.key)
						except:
							pass
						
					pygame.draw.rect(prompt, (255,255,255), (5,25, 390, 20), 0)
					textRENDER = FontDATA.render(word, True, (191,181,171))
					prompt.blit(textRENDER, (5,25))
					pygame.display.update()
					###
					
#==================#
#Promps for values
Prompt = TextEntry()
Prompt.showPrompt("Please enter your reciever pin:")
PinIn = ""
while True:
	PinIn = Prompt.getInput()
	try:
		PinIn = int(PinIn)
		break
	except:
		pass
Prompt.showPrompt("Please enter a remote name:")
remote = Prompt.getInput()

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
def showPrompt(starttext):		
		#---------#
		FontDATA = pygame.font.SysFont("Arial", 15)
		textRENDER = FontDATA.render(starttext, True, (191,181,171))
		UI.blit(textRENDER, (5,205))
		pygame.display.update()
		###
		
def getInput():
	FontDATA = pygame.font.SysFont("Arial", 15)
	word = ""
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return ''
				break
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					pygame.draw.rect(UI, (255,255,255), (5,205,200,50), 0)
					pygame.display.update()
					return word
				elif event.key == pygame.K_BACKSPACE:
					word = word[:len(word)-1]
				else:
					try:
						word = word + chr(event.key)
					except:
						pass
				pygame.draw.rect(UI, (255,255,255), (5,225, 390, 20), 0)
				textRENDER = FontDATA.render(word, True, (191,181,171))
				UI.blit(textRENDER, (5,225))
				pygame.display.update()
				###
					
def writeText(text, font, size, pos, colour): #Writes text to screen
	FontDATA = pygame.font.SysFont(font, size)
	textRENDER = FontDATA.render(text, True, colour)
	UI.blit(textRENDER, pos)
	###
	
def setShownState(text, colour): #Sets the current state shown by the indicator text
	pygame.draw.rect(UI, (255,255,255), (5, 90, 230, 20), 0)
	writeText(text, "Arial", 16, [5,90], colour)
	pygame.display.update()
	###
	
def showResults(cmd): #Shows the results of the tests on the GUI
	#Show Hex --
	writeText("Hex Command: " + str(cmd), "Arial", 14, [25,130], [0,0,0])
	#Copy Data Button --
	pygame.draw.rect(UI, (9,115,238), (5,167, 230, 30),0)
	writeText("Save Command", "Arial", 16, [66,172], [255,255,255])
	pygame.display.update()
	###

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
	pygame.draw.rect(UI, (255,255,255), (5, 110, 230, 1000),0) #Removes any results already on screen
	#Takes samples
	setShownState("Awaiting Data....", [203,58,53])
	command = ConvertHex(getData())
	setShownState("Data Recieved.", [22,207,49])
	showResults(command) #Shows results on the screen
	return command
	###
	
#==================#
#Sets up GUI
ico = pygame.image.load("res/IRIcon.png")
pygame.display.set_caption("IR Data")
pygame.display.set_icon(ico)
UI = pygame.display.set_mode((240,280))
UI.fill((255,255,255))
writeText("IR Data Collector", "Arial Bold", 40, [5,5], [0,0,0]) #Fills screen
writeText("Collect data from an IR remote", "Arial", 16, [5,35], [92,103,186])
pygame.draw.rect(UI, (203,58,53), (5,55, 230, 30),0)
writeText("Start Test", "Arial", 16, [82,60], [255,255,255])
pygame.display.update()

#==================#
#Main program loop
while True:
	for event in pygame.event.get():
		if event.type == pygame.MOUSEBUTTONDOWN: #Runs when mouse is clicked
			x, y = event.pos #Gets click location
			if y > 55 and y < 85: #Start test button
				finalData = runTest()
			if y > 167 and y < 197: #Copy data button
				showPrompt("Please enter button name:")
				output = open(remote+".txt", 'a')
				output.writelines("""
Button Code - """ + getInput() + ": " + str(finalData))
				output.close()
		if event.type == pygame.QUIT:
			GPIO.cleanup()
			exit()

