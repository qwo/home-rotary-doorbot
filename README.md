# Personal Doorbot

Make your own personal intercom ring using a raspberry pi and python!

- Raspberry pi
- 56K RJ11 Modem 

# Setup 
```
pip install -r requirements.xt
python answer.py
```

## Usage 
daemonize the process `answer.py` for long term usage.
- Currently, it picks up a call
- changes the handset to voice mode
- dials ATD0 making a connection
- Tone Presses a "6"* 

You can modify the * section to fit your own code or provide a second factor auth. Cannot get input from the client.


Shoutouts
- http://pcmicro.com/support/modem_at_commands.html
- https://stackoverflow.com/questions/23532038/read-response-at-command-with-pyserial
- https://www.raspberrypi.org/forums/viewtopic.php?t=112508#p784914
- Huge thanks for [DTMF tones article from  Pradeep Singh](https://iotbytes.wordpress.com/send-dtmf-tones-with-raspberry-pi/).