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
	# This file will be ran as sudo. Do here whatever you need to remove files and programs before app uninstall.
	conf2 = conf.Conf()
	currentdir = os.path.dirname(__file__)
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-myapp',currentLanguage)

	# here we remove the services
	print(_('Removing openplotter-read-MCS service...'))
	try:
		subprocess.call(['systemctl', 'disable', 'openplotter-MCS-read'])
		subprocess.call(['systemctl', 'stop', 'openplotter-MCS-read'])
		subprocess.call(['rm', '-f', '/etc/systemd/system/openplotter-MCS-read.service'])
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	
	try:
		fo1r = open('/boot/config.txt', "r")
		configcontent = fo1r.read()
		startpos = configcontent.find("#MCS-Openplotter config (Do not delete or edit this part)(start)")
		endpos = configcontent.find("#MCS-Openplotter config (Do not delete or edit this part)(end)")+62
		fo1r.close()
		newconfigcontent = fo1r[0:startpos]+fo1r[endpos:0]
		
		print(startpos)
		print(endpos)
		
		if (startpos != -1):
			fo1 = open('/boot/config.txt', "w")		
			fo1.write (newconfigcontent)
			fo1.close()
			print(_("config.txt entries deleted"))
		else:
			print(_("config.txt entries not exists"))

	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
