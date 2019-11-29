import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=5)
ser.write("AT\r")
response =  ser.read(2)

def tick(s=.01):
    time.sleep(s)

while True:

    response =  ser.readline()
    print (response)
    tick()
    if "RING" in response:
        ser.write("ATA\r")
        tick()
        ser.write("ATM\r")
        response =  ser.readline()
        while True:
            tick()
            response =  ser.readline()
            print(response)
            ser.write("ATD *6\r")
            tick()
            response =  ser.readline()
            print(response)
            tick()
            ser.write("ATH \r") # Goodbye



            # ser.write("ATDnnn\r") # Hello
            # ser.write("AT+VTD=*;+VTD=1;+VTD=2;+VTD=3;+VTD=4;+VTD=#\r")
            

        
