#!/usr/bin/env python3

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

import wx, os, webbrowser, subprocess, socket
import wx.richtext as rt
from openplotterSettings import conf
from openplotterSettings import language
# use the class "platform" to get info about the host system. See: https://github.com/openplotter/openplotter-settings/blob/master/openplotterSettings/platform.py
from openplotterSettings import platform

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.conf_folder = self.conf.conf_folder
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(__file__)
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-MCS',self.currentLanguage)

		wx.Frame.__init__(self, None, title=_('OpenPlotter MCS'), size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-MCS.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(102, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		toolSend = self.toolbar1.AddCheckTool(103, _('Sending Data'), wx.Bitmap(self.currentdir+"/data/send.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSend, toolSend)
		self.toolbar1.AddSeparator()
		toolOutput = self.toolbar1.AddTool(106, _('Read Configuration'), wx.Bitmap(self.currentdir+"/data/check.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolOutput, toolOutput)
		self.toolbar1.AddSeparator()
		toolApply = self.toolbar1.AddTool(104, _('Apply Changes'), wx.Bitmap(self.currentdir+"/data/apply.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolApply, toolApply)
		toolCancel = self.toolbar1.AddTool(105, _('Cancel Changes'), wx.Bitmap(self.currentdir+"/data/cancel.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolCancel, toolCancel)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.MCS_Settings = wx.Panel(self.notebook)
		self.owire = wx.Panel(self.notebook)
		self.connections = wx.Panel(self.notebook)
		self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.MCS_Settings, _('MCS Settings'))
		self.notebook.AddPage(self.owire, _('MCS-1Wire'))
		self.notebook.AddPage(self.connections, _('Data output'))
		self.notebook.AddPage(self.output, _('Output'))

		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/openplotter-MCS.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/openplotter-MCS.png", wx.BITMAP_TYPE_PNG))
		img2 = self.il.Add(wx.Bitmap(self.currentdir+"/data/connections.png", wx.BITMAP_TYPE_PNG))
		img3 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))

		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)
		self.notebook.SetPageImage(2, img2)
		self.notebook.SetPageImage(3, img3)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.pageMCS()
		self.pageowire()
		self.pageConnections()
		self.pageOutput()

		self.Centre()

		##
		self.read_sensors()

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	# red for error or cancellation messages
	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	# green for succesful messages
	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	# black for informative messages
	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK)

	# yellow for attention messages
	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0))

	def onTabChange(self, event):
		self.SetStatusText('')

	# create your page in the manuals and add the link here
	def OnToolHelp(self, event):
		url = "/usr/share/openplotter-doc/template/MCS_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event):
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def pageOutput(self):
		self.logger = rt.RichTextCtrl(self.output, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)

	def pageMCS(self):

		Info_Label = wx.StaticText(self.MCS_Settings, label=_("Settings for MCP2515 (CAN/NMEA2000) must done in CAN App. Settings for GPIO Input must done in Action App\n"))
		Info_Label.SetForegroundColour((139,37,0))

		########### read MCS CAN Interfaces
		try:
			cansetting = os.popen ("ifconfig can0")
			cansetting_in = cansetting.read()
			if "can0" not in cansetting_in:
				cansetting_in= "no CAN Device found"
		except:
			self.ShowStatusBarYELLOW(_('Cannot read ifconfig'))

		CANstat_Label = wx.StaticText(self.MCS_Settings, label=_('Available MCS-CAN Interfaces:\n '))
		CANstat_Label.SetForegroundColour((0,0,139))
		CANstat = wx.StaticText(self.MCS_Settings, label = cansetting_in)

		########### read MCS Serial Interfaces
		try:
			ser=os.listdir("/dev/")
			avser=""
			for i in ser:
				if "ttySC" in i:
					avser=i+" ; "+avser

			if "ttySC0" not in avser:
				avser= "no Serial Device found"
		except:
			self.ShowStatusBarYELLOW(_('Cannot read /dev/'))

		SERstat_Label = wx.StaticText(self.MCS_Settings, label=_('\nAvailable MCS-Serial Interfaces:\n '))
		SERstat_Label.SetForegroundColour((0,0,139))
		SERstat = wx.StaticText(self.MCS_Settings, label = avser )

		self.ShowStatusBarGREEN(_('all settings read succesful'))

		#############

		hbox = wx.BoxSizer(wx.VERTICAL)
		hbox.Add(Info_Label, 0, wx.LEFT | wx.EXPAND, 5)
		hbox.Add(CANstat_Label, 0, wx.LEFT | wx.EXPAND, 5)
		hbox.Add(CANstat, 0, wx.LEFT | wx.EXPAND, 5)
		hbox.Add(SERstat_Label, 0, wx.LEFT | wx.EXPAND, 5)
		hbox.Add(SERstat, 0, wx.LEFT | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 5)
		vbox.AddStretchSpacer(1)
		self.MCS_Settings.SetSizer(vbox)


	def pageowire(self):
		self.listSensors = wx.ListCtrl(self.owire, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.listSensors.InsertColumn(0, ' ', width=16)
		self.listSensors.InsertColumn(1, _('SensorID'), width=180)
		self.listSensors.InsertColumn(2, _('Name'), width=150)
		self.listSensors.InsertColumn(3, _('Value'), width=100)
		self.listSensors.InsertColumn(4, _('SignalK Key'), width=300)

		self.listSensors.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSensorsSelected)
		self.listSensors.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListSensorsDeselected)

		self.toolbar2 = wx.ToolBar(self.owire, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.addButton = self.toolbar2.AddTool(201, _('Add'), wx.Bitmap(self.currentdir+"/data/add.png"))
		self.Bind(wx.EVT_TOOL, self.OnAddButton, self.addButton)
		self.editButton = self.toolbar2.AddTool(202, _('Edit'), wx.Bitmap(self.currentdir+"/data/edit.png"))
		self.Bind(wx.EVT_TOOL, self.OnEditButton, self.editButton)
		self.removeButton = self.toolbar2.AddTool(203, _('Remove'), wx.Bitmap(self.currentdir+"/data/remove.png"))
		self.Bind(wx.EVT_TOOL, self.OnRemoveButton, self.removeButton)
		self.loadButton = self.toolbar2.AddTool(204, _('Refresh Value'), wx.Bitmap(self.currentdir+"/data/edit.png"))
		self.Bind(wx.EVT_TOOL, self.OnLoadButton, self.loadButton)


		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.listSensors, 1, wx.EXPAND, 0)
		sizer.Add(self.toolbar2, 0)
		self.owire.SetSizer(sizer)


######
	def read_sensors (self):
		try:
			data = self.conf.get('MCS', 'owiresensors')
			self.config_osensors = eval (data)
			if not self.config_osensors:
				self.config_osensors = []


		except:
			self.config_osensors=[]

		### read signalk_keys
		foo = open(self.currentdir+"/data/speckeys","r")
		self.avspeckeys = foo.read()
		foo.close()
		self.avspeckeys = list(self.avspeckeys.split(","))
		#####

		self.printSensors()

	def printSensors(self):
		self.onListSensorsDeselected()
		self.listSensors.DeleteAllItems()
		count=1
		for i in self.config_osensors:
			temp=""
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
			except: pass #Fehlermeldung
			if temp:
				temp=str(temp)+"°C"
			if not temp:
				temp= _("no Sensor found")

			self.listSensors.Append ([count,i[0],i[1],temp,i[2]])
			count = count + 1
#####
	def OnAddButton(self,e):
		dlg = addowire(self.config_osensors, self.avspeckeys)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			addname = dlg.name.GetValue()
			if not addname:
				self.ShowStatusBarRED(_('Failed. You must add a Sensorname.'))
				dlg.Destroy()
				return
			addID = dlg.ID
			if not addID:
				self.ShowStatusBarRED(_('Failed. You must select a Sensor.'))
				dlg.Destroy()
				return
			addsignalkkey= dlg.signalkkey.GetValue()
			if not addsignalkkey:
				self.ShowStatusBarRED(_('Failed. You must select a Signalk Key.'))
				dlg.Destroy()
				return
			newoSensor=[addID,addname,addsignalkkey]
			self.config_osensors.append(newoSensor)
		dlg.Destroy()
		self.printSensors()


	def OnEditButton(self,e):
		dlg = editowire(self.avspeckeys, str(self.selected_ID))
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			editname = dlg.name.GetValue()
			editsignalkkey = dlg.signalkkey.GetValue()
			if not editname and not editsignalkkey :
				self.ShowStatusBarRED(_('Failed. You must enter a Sensorname or a Signalk Key.'))
				dlg.Destroy()
				return
			for i in self.config_osensors:
				if i[0]==self.selected_ID:
					if editname:
						i[1]=editname
					if editsignalkkey:
						i[2]=editsignalkkey

		dlg.Destroy()
		self.printSensors()

	def OnRemoveButton(self,e):
		for i in self.config_osensors:
			if i[0]==self.selected_ID:
				ii = self.config_osensors.index(i)
				del self.config_osensors[ii]
		self.printSensors()

	def OnLoadButton(self,e):
		self.printSensors()

	def onListSensorsSelected(self,e):
		i = e.GetIndex()
		valid = e and i >= 0
		if not valid: return
		self.toolbar2.EnableTool(202,True)
		self.toolbar2.EnableTool(203,True)

		onselectedDetected = self.listSensors.GetFirstSelected()
		ii = self.listSensors.GetItem(onselectedDetected, 1)
		self.selected_ID = ii.GetText()

	def onListSensorsDeselected(self,e=0):
		self.toolbar2.EnableTool(201,True)
		self.toolbar2.EnableTool(202,False)
		self.toolbar2.EnableTool(203,False)

	def OnToolSend(self,e):
		pass
		#self.notebook.ChangeSelection(0)
		#if self.toolbar1.GetToolState(103): self.myoption.SetLabel('1')
		#else: self.myoption.SetLabel('0')

	def pageConnections(self):
		self.toolbar3 = wx.ToolBar(self.connections, style=wx.TB_TEXT)
		skConnections = self.toolbar3.AddTool(302, _('SK Connection'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.OnSkConnections, skConnections)
		self.toolbar3.AddSeparator()
		skTo0183 = self.toolbar3.AddTool(303, 'SK → NMEA 0183', wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.OnSkTo0183, skTo0183)
		skTo2000 = self.toolbar3.AddTool(304, 'SK → NMEA 2000', wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.OnSkTo2000, skTo2000)

		self.listConnections = wx.ListCtrl(self.connections, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.listConnections.InsertColumn(0, _('Type'), width=80)
		self.listConnections.InsertColumn(1, _('Mode'), width=80)
		self.listConnections.InsertColumn(2, _('Data'), width=315)
		self.listConnections.InsertColumn(3, _('Direction'), width=80)
		self.listConnections.InsertColumn(4, _('Port'), width=80)
		self.listConnections.InsertColumn(5, _('Editable'), width=80)
		self.listConnections.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onlistConnectionsSelected)
		self.listConnections.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onlistConnectionsDeselected)

		self.toolbar4 = wx.ToolBar(self.connections, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.editConnButton = self.toolbar4.AddTool(402, _('Edit'), wx.Bitmap(self.currentdir+"/data/edit.png"))
		self.Bind(wx.EVT_TOOL, self.OnEditConnButton, self.editConnButton)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.listConnections, 1, wx.EXPAND, 0)
		hbox.Add(self.toolbar4, 0)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar3, 0, wx.LEFT | wx.EXPAND, 0)
		vbox.Add(hbox, 0, wx.LEFT | wx.EXPAND, 0)
		vbox.AddStretchSpacer(1)
		self.connections.SetSizer(vbox)
		self.readConnections()
		self.printConnections()

	def readConnections(self):
		from .ports import Ports
		self.ports = Ports(self.conf, self.currentLanguage)

	def printConnections(self):
		# Check if Signal K and some plugins are installed
		if self.platform.skPort:
			self.toolbar3.EnableTool(302,True)
			self.toolbar3.EnableTool(303,True)
			if self.platform.isSKpluginInstalled('signalk-to-nmea2000'):
				self.toolbar3.EnableTool(304,True)
			else: self.toolbar3.EnableTool(304,False)
		else:
			self.toolbar3.EnableTool(302,False)
			self.toolbar3.EnableTool(303,False)
			self.toolbar3.EnableTool(304,False)
		self.toolbar4.EnableTool(402,False)

		self.listConnections.DeleteAllItems()
		enabled = self.conf.get('MCS', 'sending')
		for i in self.ports.connections:
			if i['editable'] == '1': editable = _('yes')
			else: editable = _('no')
			direction = ''
			if i['direction'] == '1': direction = _('input')
			elif i['direction'] == '2': direction = _('output')
			elif i['direction'] == '3': direction = _('both')
			self.listConnections.Append([i['type'], i['mode'], i['data'], direction, str(i['port']), editable])
			# if the connection is enabled we will set the item background to:
			# yellow for Signal K data: (255,215,0)
			# blue for NMEA 2000 data: (0,215,255)
			# green for NMEA 0183 data: (115,255,115)
			if enabled == '1': self.listConnections.SetItemBackgroundColour(self.listConnections.GetItemCount()-1,(255,215,0))

	def OnSkConnections(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/-'
		webbrowser.open(url, new=2)

	def OnSkTo0183(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/plugins/sk-to-nmea0183'
		webbrowser.open(url, new=2)

	def OnSkTo2000(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/plugins/sk-to-nmea2000'
		webbrowser.open(url, new=2)

	def OnEditConnButton(self,e):
		selected = self.listConnections.GetFirstSelected()
		if selected == -1: return
		dlg = editPort(self.ports.connections[selected]['port'])
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			self.ports.connections[selected]['port'] = dlg.port.GetValue()
			self.printConnections()
		dlg.Destroy()

	def onlistConnectionsSelected(self,e):
		i = e.GetIndex()
		valid = e and i >= 0
		if not valid: return
		if self.ports.connections[i]['editable'] == '1': self.toolbar4.EnableTool(402,True)
		else: self.toolbar4.EnableTool(402,False)

	def onlistConnectionsDeselected(self,e=0):
		self.toolbar4.EnableTool(402,False)

	def OnToolApply(self,e):

		if self.toolbar1.GetToolState(103):
			self.conf.set('MCS', 'sending', '1')
			# starts service and enables it at startup. Use self.platform.admin instead of sudo
			subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'enable'])
			self.ShowStatusBarGREEN(_('Sending data enabled'))
		else:
			self.conf.set('MCS', 'sending', '0')
			# stops service and disables it at startup. Use self.platform.admin instead of sudo
			subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'disable'])
			self.ShowStatusBarYELLOW(_('Sending data disabled'))
		for i in self.ports.connections:
			self.conf.set('MCS', i['id'], str(i['port']))

		self.conf.set('MCS', 'owiresensors', str(self.config_osensors))
		self.readConnections()
		self.printConnections()

	def OnToolCancel(self,e):
		self.ShowStatusBarRED(_('Changes canceled'))
		self.readConnections()
		self.printConnections()
		self.read_sensors()

	def OnToolOutput(self,e):
		self.logger.Clear()
		self.notebook.ChangeSelection(3)

		# Available serial Ports
		self.logger.BeginTextColour((0, 130, 0))
		self.logger.BeginBold()
		self.logger.WriteText(_('Available serial ports on MCS:'))
		self.logger.EndBold()
		self.logger.EndTextColour()
		self.logger.Newline()
		# or print any program output
		self.logger.BeginTextColour((55, 55, 55))
		command = self.platform.admin+' ls /dev/ttySC* '
		popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
		for line in popen.stdout:
			if not 'Warning' in line and not 'WARNING' in line:
				self.logger.WriteText(line)
				#self.ShowStatusBarYELLOW(_('Updating packages data, please wait... ')+line)
				self.logger.ShowPosition(self.logger.GetLastPosition())
		self.logger.EndTextColour()

		# Read CAN (ifconfig) Interfaces
		self.logger.BeginTextColour((0, 130, 0))
		self.logger.BeginBold()
		self.logger.WriteText(_('Available CAN Interface on MCS:'))
		self.logger.EndBold()
		self.logger.EndTextColour()
		self.logger.Newline()
		# or print any program output
		self.logger.BeginTextColour((55, 55, 55))
		command = self.platform.admin+' ifconfig '
		popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
		for line in popen.stdout:
			if not 'Warning' in line and not 'WARNING' in line:
				self.logger.WriteText(line)
				#self.ShowStatusBarYELLOW(_('Updating packages data, please wait... ')+line)
				self.logger.ShowPosition(self.logger.GetLastPosition())
		self.logger.EndTextColour()

################################################################################

class editPort(wx.Dialog):
	def __init__(self, port):
		wx.Dialog.__init__(self, None, title=_('Port'), size=(200,150))
		panel = wx.Panel(self)
		self.port = wx.SpinCtrl(panel, 101, min=4000, max=65536, initial=50000)
		self.port.SetValue(int(port))

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(cancelBtn, 1, wx.ALL | wx.EXPAND, 10)
		hbox.Add(okBtn, 1, wx.ALL | wx.EXPAND, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.port, 1, wx.ALL | wx.EXPAND, 10)
		vbox.Add(hbox, 0, wx.EXPAND, 0)

		panel.SetSizer(vbox)
		self.Centre()

################################################################################ New created owire

class addowire(wx.Dialog):
	def __init__(self, config_osensors1, signalkkeys):

		title = _('Add 1-Wire sensor')

		wx.Dialog.__init__(self, None, title=title, size=(450,430))
		panel = wx.Panel(self)
		label_detected = wx.StaticText(panel, label=_('detected'))
		label_info = wx.StaticText(panel, label=_('Select a senser, enter a Name and a Signalk Key'))

		label_Sensorname = wx.StaticText(panel, label=_("Sensor name:"))
		label_Signalkkey = wx.StaticText(panel, label=_("Signalk Key:"))


		self.list_detected = wx.ListCtrl(panel, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.list_detected.InsertColumn(0, _('Sensor ID'), width=330)
		self.list_detected.InsertColumn(1, _('Value'), width=330)
		self.list_detected.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectDetected)

		hline1 = wx.StaticLine(panel)

		self.name = wx.TextCtrl(panel)
		self.signalkkey = wx.ComboBox(panel, choices = signalkkeys)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK, label="Add")
		refreshBtn = wx.Button(panel, label="Refresh Value")

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(label_Signalkkey, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		hbox2.Add(self.signalkkey, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(label_Sensorname, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		hbox3.Add(self.name, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)


		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.AddStretchSpacer(1)
		hbox.Add(refreshBtn, 0, wx.ALL | wx.EXPAND, 5)
		self.Bind(wx.EVT_BUTTON,self.btnrefresh,refreshBtn)
		hbox.Add(cancelBtn, 0, wx.ALL | wx.EXPAND, 5)
		hbox.Add(okBtn, 0, wx.ALL | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(label_info, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		vbox.Add(label_detected, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		vbox.Add(hline1, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(self.list_detected, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		vbox.AddSpacer(10)
		vbox.Add(hbox3, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(hbox2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddStretchSpacer(1)
		vbox.Add(hbox, 0, wx.ALL  | wx.EXPAND, 5)

		panel.SetSizer(vbox)
		self.panel = panel


		self.config_osensors = config_osensors1
		self.refresh()
		self.Centre()
		self.ID = ""

		###
	def btnrefresh (self,e):
		self.refresh()
	def refresh (self):
		self.list_detected.DeleteAllItems()

		try:
			x= os.listdir("/sys/bus/w1/devices")
			x.remove ("w1_bus_master1")

			for i in x:
				foo = open("/sys/bus/w1/devices/"+ i +"/w1_slave","r")
				data = foo.read ()
				foo.close()
				spos=data.find("t=")
				tempx=(data[spos+2:-1])
				temp = int(tempx)/1000
				exist=0
				if self.config_osensors:
					for ii in self.config_osensors:
						if i == ii[0]:
							exist = 1
				if exist==0:
					self.list_detected.Append ([i,temp])

		except:
			self.list_detected.Append (["cannot read Sensor",""])

		###
	def onSelectDetected(self, e):
		selectedDetected = self.list_detected.GetFirstSelected()
		i = self.list_detected.GetItem(selectedDetected, 0)
		self.ID = i.GetText()


################################################################################ New created owire
class editowire(wx.Dialog):
	def __init__(self,signalkkeys,ID):
		wx.Dialog.__init__(self, None, title=_('Edit 1-Wire Name'), size=(500,220))
		panel = wx.Panel(self)

		label_Text1=wx.StaticText(panel, label=_("New data for Sensor ID: "+ID))
		self.name = wx.TextCtrl(panel)
		label_Text2=wx.StaticText(panel, label=_('New Sensor Name:'))
		label_Text3=wx.StaticText(panel, label=_('New Sensor SignalkKey:'))

		hline1 = wx.StaticLine(panel)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(label_Text2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		hbox1.Add(self.name, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		self.signalkkey = wx.ComboBox(panel, choices = signalkkeys)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(label_Text3, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		hbox2.Add(self.signalkkey, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)


		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(cancelBtn, 1, wx.ALL | wx.EXPAND, 10)
		hbox.Add(okBtn, 1, wx.ALL | wx.EXPAND, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(10)
		vbox.Add(label_Text1, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		vbox.AddSpacer(10)
		vbox.Add(hbox1, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(10)
		vbox.Add(hbox2, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(10)
		vbox.Add(hline1, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 20)
		vbox.AddSpacer(10)
		vbox.Add(hbox, 0, wx.EXPAND, 0)

		panel.SetSizer(vbox)
		self.Centre()

################################################################################

def main():
	app = wx.App()
	MyFrame().Show()
	app.MainLoop()

if __name__ == '__main__':
	main()
# new Edit
