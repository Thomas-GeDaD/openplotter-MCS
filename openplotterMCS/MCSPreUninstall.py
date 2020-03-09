#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2015 by GeDaD <https://github.com/Thomas-GeDaD/openplotter-MCS>
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
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	package = 'openplotter-MCS'
	language.Language(currentdir,package,currentLanguage)

	print(_('Removing app from OpenPlotter...'))
	try:
		externalApps0 = eval(conf2.get('APPS', 'external_apps'))
		externalApps1 = []
		for i in externalApps0:
			if i['package'] != package: externalApps1.append(i)
		conf2.set('APPS', 'external_apps', str(externalApps1))
		os.system('rm -f /etc/apt/sources.list.d/MCS.list') ### replace myapp.list by the name of your sources file (see myappPostInstall.py script).
		os.system('apt update')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
	
	
	# here we remove the services
	print(_('Removing openplotter-read-MCS service...'))
	try:
		subprocess.call(['systemctl', 'disable', 'openplotter-MCS-read'])
		subprocess.call(['systemctl', 'stop', 'openplotter-MCS-read'])
		subprocess.call(['rm', '-f', '/etc/systemd/system/openplotter-MCS-read.service'])
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
	
	### Remove autoshutdown Service
	print(_('Removing openplotter-autoshutdown Service...'))
	try:
		subprocess.call(['systemctl', 'disable', 'openplotter-MCS-asd'])
		subprocess.call(['systemctl', 'stop', 'openplotter-MCS-asd'])
		subprocess.call(['rm', '-f', '/etc/systemd/system/openplotter-MCS-asd.service'])
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))	
	
	try:
		fo1r = open('/boot/config.txt', "r")
		configcontent = fo1r.read()
		startpos = configcontent.find("#MCS-Openplotter config (Do not delete or edit this part)(start)")
		endpos = configcontent.find("#MCS-Openplotter config (Do not delete or edit this part)(end)")+63
		fo1r.close()
		before=""
		behind=""
		before = configcontent[:startpos]
		behind = configcontent[endpos:]
		newconfigcontent = before+behind
				
		if (startpos != -1):
			fo1 = open('/boot/config.txt', "w")		
			fo1.write (newconfigcontent)
			fo1.close()
			print(_("config.txt entries deleted"))
		else:
			print(_("config.txt entries not exists"))

	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Removing version...'))
	try:
		conf2.set('APPS', 'mcs', '')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
