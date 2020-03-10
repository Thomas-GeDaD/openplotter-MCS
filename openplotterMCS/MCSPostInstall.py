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
import os, subprocess, sys
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from .version import version

def main():
	# This file will be ran as sudo. Do here whatever you need after package installation.

	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	package= 'openplotter-mcs'
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,package,currentLanguage)
	platform2 = platform.Platform()
	

	app = {
	'name': 'MCS',
	'platform': 'rpi', ### rpi, debian or both
	'package': package,
	'preUninstall': platform2.admin+' '+'MCSPreUninstall',
	'uninstall': package,
	'sources': ['https://dl.cloudsmith.io/public/thomas-gersmann/openplotter-mcs/deb/debian buster'], ### replace by your repositories URLs separated by commas.
	'dev': 'no', ### set to "yes" if you do not want your app to be updated from repositories yet.
	'entryPoint': 'openplotter-MCS',
	'postInstall': platform2.admin+' '+'MCSPostInstall',
	'reboot': 'yes',
	'module': 'openplotterMCS' ### replace by your python module name (see setup.py file).
	}
	gpgKey = currentdir+'/data/MCS.gpg.key' ### replace by the path to your gpg key file. Replace contents of this file by your key.
	sourceList = currentdir+'/data/MCS.list' ### replace by the path to your sources list file. Replace contents of this file by your packages sources.

	#########################
	print(_('Adding MCS-app to OpenPlotter...'))
	try:
		try:
			externalApps0 = eval(conf2.get('APPS', 'external_apps'))
		except: externalApps0 = []
		externalApps1 = []
		for i in externalApps0:
			if i['package'] != package: externalApps1.append(i)
		externalApps1.append(app)
		conf2.set('APPS', 'external_apps', str(externalApps1))
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))	
	
	
	print(_('Checking sources...'))
	try:
		sources = subprocess.check_output('apt-cache policy', shell=True).decode(sys.stdin.encoding)
		exists = True
		for i in app['sources']:
			if not i in sources: exists = False
		if not exists:
			os.system('cp '+sourceList+' /etc/apt/sources.list.d')
			os.system('apt-key add - < '+gpgKey)
			os.system('apt update')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
	
	
	############Start
	print(_('Adding openplotter-read-MCS service...'))
	###add Service
	try:
		fo = open('/etc/systemd/system/openplotter-MCS-read.service', "w")
		fo.write( '[Service]\nExecStart=openplotter-MCS-read\nStandardOutput=syslog\nStandardError=syslog\nUser='+conf2.user+'\n[Install]\nWantedBy=multi-user.target')
		fo.close()
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
	
	###### add Openplotter autoshutdown service
	print(_('Adding openplotter-autoshutdown Service...'))
	
	try:
		fo = open('/etc/systemd/system/openplotter-MCS-asd.service', "w")
		fo.write( '[Service]\nExecStart=openplotter-MCS-asd\nStandardOutput=syslog\nStandardError=syslog\nUser='+conf2.user+'\n[Install]\nWantedBy=multi-user.target')
		fo.close()
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))


	####### /boot/config.txt edit for SC16is752 and (MCP2515)

	print(_('Adding config.txt entries...'))

	try:
		fo1r = open('/boot/config.txt', "r")
		configcontent = fo1r.read()
		startpos = configcontent.find("#MCS-Openplotter config (Do not delete or edit this part)(start)")
		fo1r.close()
		#print(_(startpos))
		
		if (startpos == -1):
			fo1 = open('/boot/config.txt', "a")
			fo1.write ("\n")
			fo1.write ("#MCS-Openplotter config (Do not delete or edit this part)(start)\n")
			#fo1.write ("dtoverlay=mcp2515-can1,oscillator=16000000,interrupt=25\n")
			#fo1.write ("dtoverlay=spi-bcm2835-overlay\n")
			fo1.write ("dtoverlay=sc16is752-i2c,int_pin=13,addr=0x4c,xtal=14745600\n")
			fo1.write ("dtoverlay=sc16is752-i2c,int_pin=12,addr=0x49,xtal=14745600\n")
			fo1.write ("dtoverlay=sc16is752-i2c,int_pin=6,addr=0x48,xtal=14745600\n")
			fo1.write ("#MCS-Openplotter config (Do not delete or edit this part)(end)\n")
			fo1.close()
			print(_("config.txt entries created"))
		else:
			print(_("config.txt entries already exists"))

	except Exception as e: print(_('FAILED: ')+str(e))
	
	######added 1-wire modules
	print(_('Adding modules to /etc/modules...'))
	
	try:
		modulesr = open("/etc/modules","r")
		strg=modulesr.read()
		modulesr.close()
		i2c_dev = strg.find("i2c-dev")
		ds2482 = strg.find("ds2482")
		wire = strg.find("wire")
		
		modules = open("/etc/modules","a")
		#######added i2c-dev
		if (i2c_dev==-1):
			modules.write ("\ni2c-dev")
			print(_("i2c-dev added to modules"))
		else:
			print(_("i2c-dev already exists"))
		#######added ds2482
		if (ds2482==-1):
			modules.write ("\nds2482")
			print(_("ds2482 added to modules"))
		else:
			print(_("ds2482 already exists"))
		#######added wire
		if (wire==-1):
			modules.write ("\nwire")
			print(_("wire added to modules"))
		else:
			print(_("wire already exists"))
		
		modules.close()
			
	except Exception as e: print(_('FAILED: ')+str(e))
		
	print(_('Setting version...'))
	try:
		conf2.set('APPS', 'mcs', version)
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
	
if __name__ == '__main__':

	main()


