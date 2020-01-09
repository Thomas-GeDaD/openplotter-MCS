#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by GeDaD https://github.com/Thomas-GeDaD/openplotter-MCS
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

from setuptools import setup
from openplotterMCS import version

setup (
	name = 'openplotterMCS',
	version = version.version,
	description = 'This is a App for the MCS board',
	license = 'GPLv3',
	author="Thomas Gersmann",
	author_email='t.gersmann@gedad.de',
	url='https://github.com/Thomas-GeDaD/openplotter-MCS',
	packages=['openplotterMCS'],
	classifiers = ['Natural Language :: English',
	'Operating System :: POSIX :: Linux',
	'Programming Language :: Python :: 3'],
	include_package_data=True,
	entry_points={'console_scripts': ['openplotter-MCS=openplotterMCS.openplotterMCS:main','openplotter-MCS-read=openplotterMCS.openplotterMCSRead:main','openplotter-MCS-asd=openplotterMCS.openplotterMCSasd:main','MCSPostInstall=openplotterMCS.MCSPostInstall:main','MCSPreUninstall=openplotterMCS.MCSPreUninstall:main']},
	data_files=[('share/applications', ['openplotterMCS/data/openplotter-MCS.desktop']),('share/pixmaps', ['openplotterMCS/data/openplotter-MCS.png']),],
	)
