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
from openplotterSettings import conf

# this file runs as a service in the background
def main():
	try:
		conf2 = conf.Conf()
		value = conf2.get('MCS', 'sending')
		port = conf2.get('MCS', 'MCSConn1')
		Sensor = conf2.get('MCS', 'owiresensors')
		config_osensors = eval (Sensor)
		
		if value == '1':
			# this script sends data to Signal K servers by an UDP connection in client mode
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			while True:
				values=""
			
				###########			
				for i in config_osensors:
					try:
						x= os.listdir("/sys/bus/w1/devices")
						x.remove ("w1_bus_master1")

						for ii in x:
							if ii ==i[0]:
								foo = open("/sys/bus/w1/devices/"+ ii +"/w1_slave","r")
								data = foo.read ()
								foo.close()
								spos=data.find("t=")
								tempx=(data[spos+2:-1])
								temp = int(tempx)/1000
					except Exception as e: print (str(e))
								
					values += '{"path":"'+ str(i[2]) +'","value":' +str(temp)+ '},'
			
			
			############
				values=values[0:-1]
				SignalK = '{"updates":[{"source":"OpenPlotter-MCS-OWire","values":['+values+']}]}\n'		
				sock.sendto(SignalK.encode('utf-8'), ('127.0.0.1', int(port)))
				time.sleep(2)
	except Exception as e: print (str(e))

if __name__ == '__main__':
	main()
