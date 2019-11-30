
##------------------------------------------
##--- Author: Pradeep Singh
##--- Blog: https://iotbytes.wordpress.com/send-dtmf-tones-with-raspberry-pi/
##--- Date: 29th June 2018
##--- Version: 1.0
##--- Python Ver: 2.7
##--- Description: This python script would dial a phone number and pass the DTMF digits using Raspberry Pi and USRobotics USR5637 USB Dial-up Modem.
##--- Hardware: Raspberry Pi3 and USRobotics USR5637 USB Modem
##------------------------------------------


import serial
import time
import threading
import atexit
import sys
import re
import wave
from datetime import datetime
import os
import fcntl
import subprocess


#=================================================================
# Set these variables 
#=================================================================
PHONE_NUMBER = "xx" # Enter the Phone number that you want to dial
DTMF_DIGITS = "6666" # Enter the DTMF digits that you want to pass (valid options: 0-9, * and #)
#=================================================================



MODEM_RESPONSE_READ_TIMEOUT = 120  #Time in Seconds (Default 120 Seconds)
MODEM_NAME = 'U.S. Robotics'    # Modem Manufacturer, For Ex: 'U.S. Robotics' if the 'lsusb' cmd output is similar to "Bus 001 Device 004: ID 0baf:0303 U.S. Robotics"

# Used in global event listener
disable_modem_event_listener = True

# Global Modem Object
analog_modem = serial.Serial()

#=================================================================
# Set COM Port settings
#=================================================================
def set_COM_port_settings(com_port):
	analog_modem.port = com_port
	analog_modem.baudrate = 57600 #9600 #115200
	analog_modem.bytesize = serial.EIGHTBITS #number of bits per bytes
	analog_modem.parity = serial.PARITY_NONE #set parity check: no parity
	analog_modem.stopbits = serial.STOPBITS_ONE #number of stop bits
	analog_modem.timeout = 3            #non-block read
	analog_modem.xonxoff = False     #disable software flow control
	analog_modem.rtscts = False     #disable hardware (RTS/CTS) flow control
	analog_modem.dsrdtr = False      #disable hardware (DSR/DTR) flow control
	analog_modem.writeTimeout = 3     #timeout for write
#=================================================================



#=================================================================
# Detect Com Port
#=================================================================
def detect_COM_port():

	# List all the Serial COM Ports on Raspberry Pi
	proc = subprocess.Popen(['ls /dev/ttyACM0*'], shell=True, stdout=subprocess.PIPE)
	com_ports = proc.communicate()[0]
	com_ports_list = com_ports.split('\n')

	# Find the right port associated with the Voice Modem
	for com_port in com_ports_list:
		if 'tty' in com_port:
			#Try to open the COM Port and execute AT Command
			try:
				# Set the COM Port Settings
				set_COM_port_settings(com_port)
				analog_modem.open()
			except:
				print "Unable to open COM Port: " + com_port
				pass
			else:
				#Try to put Modem in Voice Mode
				if not exec_AT_cmd("AT+FCLASS=8", "OK"):
					print "Error: Failed to put modem into voice mode."
					if analog_modem.isOpen():
						analog_modem.close()
				else:
					# Found the COM Port exit the loop
					print "Modem COM Port is: " + com_port
					analog_modem.flushInput()
					analog_modem.flushOutput()
					break
#=================================================================



#=================================================================
# Initialize Modem
#=================================================================
def init_modem_settings():
	
	# Detect and Open the Modem Serial COM Port
	try:
		detect_COM_port()
	except:
		print "Error: Unable to open the Serial Port."
		sys.exit()

	# Initialize the Modem
	try:
		# Flush any existing input outout data from the buffers
		analog_modem.flushInput()
		analog_modem.flushOutput()

		# Test Modem connection, using basic AT command.
		if not exec_AT_cmd("AT"):
			print "Error: Unable to access the Modem"

		# reset to factory default.
		if not exec_AT_cmd("ATZ3"):
			print "Error: Unable reset to factory default"			
			
		# Display result codes in verbose form 	
		if not exec_AT_cmd("ATV1"):
			print "Error: Unable set response in verbose form"	

		# Enable Command Echo Mode.
		if not exec_AT_cmd("ATE1"):
			print "Error: Failed to enable Command Echo Mode"		

		# Enable formatted caller report.
		if not exec_AT_cmd("AT+VCID=1"):
			print "Error: Failed to enable formatted caller report."
			
		# Flush any existing input outout data from the buffers
		analog_modem.flushInput()
		analog_modem.flushOutput()

	except:
		print "Error: unable to Initialize the Modem"
		sys.exit()
#=================================================================



#=================================================================
# Execute AT Commands at the Modem
#=================================================================
def exec_AT_cmd(modem_AT_cmd, expected_response="OK"):
	
	global disable_modem_event_listener
	disable_modem_event_listener = True
	
	try:
		# Send command to the Modem
		analog_modem.write((modem_AT_cmd + "\r").encode())

		# Read Modem response
		execution_status = read_AT_cmd_response(expected_response)
		
		disable_modem_event_listener = False

		# Return command execution status
		return execution_status

	except:
		disable_modem_event_listener = False
		print "Error: Failed to execute the command"
		return False		
#=================================================================



#=================================================================
# Read AT Command Response from the Modem
#=================================================================
def read_AT_cmd_response(expected_response="OK"):
	
	# Set the auto timeout interval
	start_time = datetime.now()

	try:
		while 1:
			# Read Modem Data on Serial Rx Pin
			modem_response = analog_modem.readline()
			print modem_response
			# Recieved expected Response
			if expected_response in modem_response.strip(' \t\n\r' + chr(16)):
				return True
			# Failed to execute the command successfully
			elif "ERROR" in modem_response.strip(' \t\n\r' + chr(16)):
				return False
			elif "NO ANSWER" in modem_response.strip(' \t\n\r' + chr(16)):
				return False
			# Timeout
			elif (datetime.now()-start_time).seconds > MODEM_RESPONSE_READ_TIMEOUT:
				return False


	except:
		print "Error in read_modem_response function..."
		return False
#=================================================================





#=================================================================
# Pass DTMF Digits
#=================================================================
def pass_dtmf_digits(dtmf_digits):

	# set the default duration/length for DTMF/tone generation in 0.01 (miliseconds) s increments.
	# The default tone duration is 100 (1 second).
	DTMF_TONE_DURATION = 100

	# Gep between two DTMF Digit generation in seconds (default 1 sec)
	# Change this timer to add gap between DTMF Digits
	GAP_BETWEEN_TWO_DTMF_DIGITS = 1

	# Fixed DTMF Tones (DTMF Frequencies generated on Key press)
	DTMF_TONES_FREQUENCIES = {'1':['697','1209'],
				  '2':['697','1336'],
				  '3':['697','1477'],
				  '4':['770','1209'],
				  '5':['770','1336'],
				  '6':['770','1477'],
				  '7':['852','1209'],
				  '8':['852','1336'],
				  '9':['852','1477'],
				  '0':['941','1336'],
				  '*':['941','1209'],
				  '#':['941','1477']	
				}


	for dtmf_digit in dtmf_digits:

		# The valid single characters are 0 - 9, #, *.
		# Generates DTMF tone according to the passed characters.
		print "Generating DTMF tone for: " + str(dtmf_digit)
		freq1 = DTMF_TONES_FREQUENCIES[dtmf_digit][0]
		freq2 = DTMF_TONES_FREQUENCIES[dtmf_digit][1]
		if not exec_AT_cmd("AT+VTS=[" + freq1 + "," + freq2 + "," + str(DTMF_TONE_DURATION) + "]"):
			print "Error: Failed to pass DTMF Digit : " + str(dtmf_digit)
		
		time.sleep(GAP_BETWEEN_TWO_DTMF_DIGITS)		
#=================================================================



#=================================================================
# Dial a Number and Pass DTMF Digits
#=================================================================
def dial_n_pass_dtmf(phone_number, dtmf_digits):

	# Set number of seconds modem waits before dialling. 
	# If Xn is set to X2 or X4, this is time-out length if no dial tone.
	if not exec_AT_cmd("ATS6=2"):
		print "Error: Failed to set S6 Register value..."

	# Set number of seconds modem waits for a carrier. 
	# May be increased as needed, for example to allow modem time to establish an international connection.
	if not exec_AT_cmd("ATS7=30"):
		print "Error: Failed to set S7 Register value..."

	# Sets duration, in seconds, for pause option in the Dial command. Valid range is 0 to 32.
	if not exec_AT_cmd("ATS8=1"):
		print "Error: Failed to set S8 Register value..."

	# Sets duration, in tenths of a second, that modem waits to hang up after loss of carrier. 
	# This guard time allows your modem to distinguish a line disturbance from a true disconnect (hang up) by the remote modem. 
	# Note: If you set S10 = 255, the modem will not hang up when carrier is lost. Dropping DTR hangs up the modem.
	if not exec_AT_cmd("ATS10=60"):
		print "Error: Failed to set S10 Register value..."

	# Set duration and spacing, in milliseconds, of dialled tones.
	if not exec_AT_cmd("ATS11=95"):
		print "Error: Failed to set S11 Register value..."

	# Put Modem into Voice Mode
	if not exec_AT_cmd("AT+FCLASS=8"):
		print "Error: Failed to put modem into Voice Mode..."

	# Dial the Phone Number
	# The maximum length of a dial string is 60 characters.
        if not exec_AT_cmd("ATD" + phone_number):
		print "Error: Unable to connect with the phone number : " + phone_number
	else:
		print "Phone connected..."

		time.sleep(.5)

		# Start Generating/Passing DTMF Digits
		pass_dtmf_digits(dtmf_digits)

		# wait for a second before closing the call.
		time.sleep(1)

		#At this point close_modem_port() function will be called
		# by the "atexit" method, which will dtop the call by
		# issuing "ATH" command and close the serial port.

#=================================================================



#=================================================================
# Close the Serial Port
#=================================================================
def close_modem_port():

	# Try to close any active call
	try:
		exec_AT_cmd("ATH")
	except:
		pass

	# Close the Serial COM Port
	try:
		if analog_modem.isOpen():
			analog_modem.close()
			print ("Serial Port closed...")
	except:
		print "Error: Unable to close the Serial Port."
		sys.exit()
#=================================================================


# Main Function
 #init_modem_settings()

# Close the Modem Port when the program terminates
  # atexit.register(close_modem_port)

# Dial the number and pass the DTMF Digits 
# dial_n_pass_dtmf(PHONE_NUMBER, DTMF_DIGITS)

# print('repeating')
"""
while True:
    result = exec_AT_cmd("AT", "RING")
    print(result)
    if result:
     exec_AT_cmd("ATA")
     dial_n_pass_dtmf(PHONE_NUMBER, DTMF_DIGITS)
"""



