#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2019 by GeDaD <https://github.com/Thomas-GeDaD/openplotter-MCS>
# 
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.
import socket, time, random, os
import RPi.GPIO as GPIO
from openplotterSettings import conf

# this file runs as a service in the background
def main():
	try:
		conf2 = conf.Conf()
		value = conf2.get('MCS', 'asd_state')
		if not value : Value = "False"
		enable = eval (value)
		
		#### GPIO Config
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(5, GPIO.IN)
		start=GPIO.input(5)
		print ("asd dienst gestartet")
		print (enable, start)
		
		
		if enable and start ="1":

			while True:
				print("asd im while")
				if GPIO.input(5) == "0" 
					time.sleep(2)
					if GPIO.input(5) == "0"
						#os.system("sudo shutdown -h now")
						os.system("sudo reboot")
				
				
			time.sleep(2)
	except Exception as e: print (str(e))

if __name__ == '__main__':
	main()

