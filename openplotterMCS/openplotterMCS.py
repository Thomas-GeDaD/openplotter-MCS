#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2015 by GeDaD <hhttps://github.com/Thomas-GeDaD/openplotter-MCS>
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
import os, subprocess
from openplotterSettings import conf
from openplotterSettings import language

def main():



	# This file will be ran as sudo. Do here whatever you need after package installation.

	conf2 = conf.Conf()
	currentdir = os.path.dirname(__file__)
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-myapp',currentLanguage)

	# here we create a service to run openplotter-MCS-read file

	print(_('Adding openplotter-read-MCS service...'))
	
	try:
		fo = open('/etc/systemd/system/openplotter-MCS-read.service', "w")
		fo.write( '[Service]\nExecStart=openplotter-MCS-read\nStandardOutput=syslog\nStandardError=syslog\nUser='+conf2.user+'\n[Install]\nWantedBy=multi-user.target')
		fo.close()
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))


	####### /boot/config.txt edit for SC16is752 and MCP2515

	print(_('Adding config.txt entries...'))

	try:
		fo1r = open('/boot/config.txt', "r")
		configcontent = fo1r.read()
		startpos = configcontent.find("#MCS-Openplotter config (Do not delete or edit this part)(start)")
		fo1r.close()
		print(_(startpos))
		
		if (startpos == -1):
			fo1 = open('/boot/config.txt', "a")
			fo1.write ("\n\n\n")
			fo1.write ("#MCS-Openplotter config (Do not delete or edit this part)(start)\n")
			fo1.write ("dtoverlay=mcp2515-can1,oscillator=16000000,interrupt=25\n")
			fo1.write ("dtoverlay=spi-bcm2835-overlay\n")
			fo1.write ("dtoverlay=sc16is752-i2c,int_pin=13,addr=0x4A,xtal=14745600\n")
			fo1.write ("dtoverlay=sc16is752-i2c,int_pin=12,addr=0x49,xtal=14745600\n")
			fo1.write ("dtoverlay=sc16is752-i2c,int_pin=6,addr=0x48,xtal=14745600\n")
			fo1.write ("#MCS-Openplotter config (Do not delete or edit this part)(end)\n")
		fo1.close()

		print(_("config.txt entries created"))

	except Exception as e: print(_('FAILED: ')+str(e))
	
	####### add CAN Interface for MCP2515 CAN0
	
	try:
		fo2r = open ("/etc/network/interfaces", "r")
		interfacecontent= fo2r.read()
		intava = interfacecontent.find ("source /etc/network/interfaces.d/*")
		fo2r.close()
		print (_(intava))
		
		if (inava == -1)
			fo2 = open ("/etc/network/interfaces", "a")
			fo2.write = ("\nsource /etc/network/interfaces.d/")
			fo2.close()
		print(_("interface.d appended"))
		
		fo3 = open ("/etc/network/interfaces/interfaces.d/can0" "w")
		fo3.write ("#physical can interfaces\nallow-hotplug can0\niface can0 can static\nbitrate 250000\ndown /sbin/ip link set $IFACE down\nup /sbin/ifconfig $IFACE txqueuelen 10000")
		fo3.close()
		print(_("interface.d can0 created")
		
if __name__ == '__main__':



	main()
