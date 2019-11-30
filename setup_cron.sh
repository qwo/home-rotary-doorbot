#!/bin/bash

(crontab -l ; echo "*/5 * * * * pgrep -f answer.py || nohup python /home/pi/Code/answer.py > test.out" ) | crontab 