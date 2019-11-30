import serial
import time
import pass_dtmf_tones as df 



ser = serial.Serial('/dev/ttyACM0', 115200, timeout=5)
ser.write("AT\r")
response =  ser.read(2)
notDone = True

def tick(s=.01):
    time.sleep(s)

def do_command(cmd):
    ser.write(cmd)

    response = ser.readline()
    print (response)
    tick()
    return response 


while notDone:
    # do_command("ATA\r");
    response =  ser.readline()
    print (response)
    tick()
    if "R" in response:
        do_command("AT;\r") # Hello
        # do_command("ATM\r") # Audio
        while True:
            # do_command(input())
            df.init_modem_settings()
            df.dial_n_pass_dtmf("","6")
            df.atexit.register(df.close_modem_port)
            break;
        # notDone = False
        print('exiting')
        ser.write('ATH;\r')
    
        
