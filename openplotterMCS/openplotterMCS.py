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

import wx, os, webbrowser, subprocess, socket, time
import wx.richtext as rt
from openplotterSettings import conf
from openplotterSettings import language
# use the class "platform" to get info about the host system. See: https://github.com/openplotter/openplotter-settings/blob/master/openplotterSettings/platform.py
from openplotterSettings import platform
from .version import version

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.conf_folder = self.conf.conf_folder
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(__file__)
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-MCS',self.currentLanguage)

		wx.Frame.__init__(self, None, title='MCS '+version, size=(800,520))
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
		self.support = wx.Panel(self.notebook)
		self.connections = wx.Panel(self.notebook)
		self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.MCS_Settings, _('MCS Settings'))
		self.notebook.AddPage(self.owire, _('MCS-1Wire'))
		self.notebook.AddPage(self.support, _('Support'))
		self.notebook.AddPage(self.connections, _('Data output'))
		self.notebook.AddPage(self.output, _('Output'))

		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/openplotter-settings.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/1-w.png", wx.BITMAP_TYPE_PNG))
		img2 = self.il.Add(wx.Bitmap(self.currentdir+"/data/openplotter-MCS.png", wx.BITMAP_TYPE_PNG))
		img3 = self.il.Add(wx.Bitmap(self.currentdir+"/data/connections.png", wx.BITMAP_TYPE_PNG))
		img4 = self.il.Add(wx.Bitmap(self.currentdir+"/data/output.png", wx.BITMAP_TYPE_PNG))

		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)
		self.notebook.SetPageImage(2, img2)
		self.notebook.SetPageImage(3, img3)
		self.notebook.SetPageImage(4, img4)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)
		
		self.pageMCS()
		self.pageowire()
		self.pagesupport()
		self.pageConnections()
		self.pageOutput()
		self.readMCS()
		self.read_sensors()
		self.readwic()

		self.Centre()
		
		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()
		

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

		#----------------------------------Pages-------------------------------------#
	def pageOutput(self):
		self.logger = rt.RichTextCtrl(self.output, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.logger, 1, wx.EXPAND, 0)
		self.output.SetSizer(sizer)
	def pageMCS(self):
		# Checkbox for Autoshutdown
		autoshutd_Label = wx.StaticText(self.MCS_Settings, label=_('Enable Auto-Shutdown by Digital Input:'))
		autoshutd_Label.SetForegroundColour((0,0,139))
		
		self.cbasd = wx.CheckBox(self.MCS_Settings, label=_('Enable Autoshutdown'))
		
		## Widget Input conf:
		self.choices_digin= ["propulsion.*.revolutions","electrical.inverters.*.ac.frequency","electrical.alternators.*.revolutions"]
		self.choices_type= ["disable","frequency"]
		widget_input_label = wx.StaticText(self.MCS_Settings, label=_('Widget to configure digital inputs based on MCS (IN1-IN4) :'))
		widget_input_label.SetForegroundColour((0,0,139))
		self.widget_input_state = wx.CheckBox(self.MCS_Settings, label=_('Enable Input Widget'))
		#
		widget_input1_label = wx.StaticText(self.MCS_Settings, label=_('In1:'))
		self.widget_func1 = wx.ComboBox(self.MCS_Settings, choices = self.choices_type)
		self.widget_signalkkey1 = wx.ComboBox(self.MCS_Settings, choices = self.choices_digin)
		widget_input_label_end1 = wx.StaticText(self.MCS_Settings, label=_('Factor:'))
		self.widget_factor1 = wx.TextCtrl(self.MCS_Settings, value="1")
		
		widget_input2_label = wx.StaticText(self.MCS_Settings, label=_('In2:'))
		self.widget_func2 = wx.ComboBox(self.MCS_Settings, choices = self.choices_type)
		self.widget_signalkkey2 = wx.ComboBox(self.MCS_Settings, choices = self.choices_digin)
		widget_input_label_end2 = wx.StaticText(self.MCS_Settings, label=_('Factor:'))
		self.widget_factor2 = wx.TextCtrl(self.MCS_Settings, value="1")
		
		widget_input3_label = wx.StaticText(self.MCS_Settings, label=_('In3:'))
		self.widget_func3 = wx.ComboBox(self.MCS_Settings, choices = self.choices_type)
		self.widget_signalkkey3 = wx.ComboBox(self.MCS_Settings, choices = self.choices_digin)
		widget_input_label_end3 = wx.StaticText(self.MCS_Settings, label=_('Factor:'))
		self.widget_factor3 = wx.TextCtrl(self.MCS_Settings, value="1")
		
		widget_input4_label = wx.StaticText(self.MCS_Settings, label=_('In4:'))
		self.widget_func4 = wx.ComboBox(self.MCS_Settings, choices = self.choices_type)
		self.widget_signalkkey4 = wx.ComboBox(self.MCS_Settings, choices = self.choices_digin)
		widget_input_label_end4 = wx.StaticText(self.MCS_Settings, label=_('Factor:'))
		self.widget_factor4 = wx.TextCtrl(self.MCS_Settings, value="1")
		#	
		hbox1 = wx.GridBagSizer(3, 4)
		hbox1.Add(widget_input1_label, pos=(0,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_func1, pos=(0,1),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_signalkkey1, pos=(0,2),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(widget_input_label_end1, pos=(0,3),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_factor1, pos=(0,4),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		
		hbox1.Add(widget_input2_label, pos=(1,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_func2, pos=(1,1),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_signalkkey2, pos=(1,2),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(widget_input_label_end2, pos=(1,3),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_factor2, pos=(1,4),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		
		hbox1.Add(widget_input3_label, pos=(2,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_func3, pos=(2,1),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_signalkkey3, pos=(2,2),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(widget_input_label_end3, pos=(2,3),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_factor3, pos=(2,4),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		
		hbox1.Add(widget_input4_label, pos=(3,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_func4, pos=(3,1),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_signalkkey4, pos=(3,2),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(widget_input_label_end4, pos=(3,3),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		hbox1.Add(self.widget_factor4, pos=(3,4),flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL,border=5)
		#
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(autoshutd_Label, 0, wx.LEFT | wx.EXPAND, 0)
		vbox.Add(self.cbasd, flag=wx.TOP|wx.LEFT, border=10)
		vbox.AddSpacer(5)
		vbox.Add(wx.StaticLine(self.MCS_Settings), 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 0)
		vbox.AddSpacer(5)
		vbox.Add(widget_input_label, 0, wx.LEFT | wx.EXPAND, 0)
		vbox.AddSpacer(5)
		vbox.Add(self.widget_input_state, 0, wx.LEFT | wx.EXPAND, 10)
		vbox.Add(hbox1, 0, wx.ALL | wx.EXPAND, 5)
		
		self.MCS_Settings.SetSizer(vbox)
		
		self.read_asd()
		

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

	def pagesupport(self):
		Info_Label = wx.StaticText(self.support, label=_("Settings for MCP2515 (CAN/NMEA2000) must done in CAN App. Settings for GPIO Input must done in Action App\n"))
		Info_Label.SetForegroundColour((0,0,139))

		# read MCS CAN Interfaces
		try:
			cansetting = os.popen ("ifconfig can0 | sed -n 1,1p")
			cansetting_in = cansetting.read()
			if "can0" not in cansetting_in:
				cansetting_in= "no CAN Device found"
		except:
			self.ShowStatusBarYELLOW(_('Cannot read ifconfig'))

		CANstat_Label = wx.StaticText(self.support, label=_('Available MCS-CAN Interfaces: '))
		CANstat_Label.SetForegroundColour((0,0,139))
		CANstat = wx.StaticText(self.support, label = cansetting_in)

		########### read MCS Serial Interfaces
		try:
			ser=os.listdir("/dev/")
			avser=""
			for i in ser:
				if "ttySC" in i:
					avser=i+" ; "+avser

			if "ttySC0" not in avser:
				avser= "no Serial Device found, MCP2515 in OP CAN App set?"
		except:
			self.ShowStatusBarYELLOW(_('Cannot read /dev/'))

		SERstat_Label = wx.StaticText(self.support, label=_('Available MCS-Serial Interfaces: '))
		SERstat_Label.SetForegroundColour((0,0,139))
		SERstat = wx.StaticText(self.support, label = avser )
		
		########### install anydesk
		AD_Label = wx.StaticText(self.support, label=_("For further assistance and for remote use you can install Anydesk. For non commercial use it´s free Software:"))
		AD_Label.SetForegroundColour((0,0,139))
		

		
		self.btnai=wx.Button(self.support, id=401, label="Install Anydesk")
		self.Bind(wx.EVT_BUTTON, self.onBtnai, self.btnai)
		self.btnas=wx.Button(self.support, id=402, label="Start Anydesk")
		self.Bind(wx.EVT_BUTTON, self.onBtnas, self.btnas)
		self.btnap=wx.Button(self.support, id=403, label="Deinstall Anydesk")
		self.Bind(wx.EVT_BUTTON, self.onBtnap, self.btnap)
		
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.btnai,0,wx.ALIGN_RIGHT)
		hbox1.Add(self.btnas,0,wx.ALIGN_LEFT)
		hbox1.Add(self.btnap,0,wx.ALIGN_RIGHT)
		
		

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(Info_Label, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(CANstat_Label, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(CANstat, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(wx.StaticLine(self.support), 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.Add(SERstat_Label, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(SERstat, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(wx.StaticLine(self.support), 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)

		vbox.Add(AD_Label, 0, wx.LEFT | wx.EXPAND, 5)
		vbox.Add(hbox1, 0, wx.ALL | wx.EXPAND, 5)

		self.support.SetSizer(vbox)
		
		self.readAD()
		
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
		
		#----------------------------------button actions-------------------------------------#
	def onBtnai (self,e): #install anydesk
		self.logger.Clear()
		self.notebook.ChangeSelection(4)
		
		ADversion= "anydesk_5.5.4-1_armhf.deb" #anydesk version
		command = self.platform.admin+' wget https://download.anydesk.com/rpi/'+ADversion+' -P '+self.currentdir+'&& '+self.platform.admin+' apt install '+self.currentdir+'/'+ADversion+' -y && '+self.platform.admin+' rm '+self.currentdir+'/'+ADversion
		popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
		for line in popen.stdout:
			self.logger.WriteText(line)
			self.ShowStatusBarYELLOW(_('Installing, please wait... ')+line)
			self.logger.ShowPosition(self.logger.GetLastPosition())
		self.conf.set('MCS', 'anydesk', '1')
		self.ShowStatusBarGREEN(_('Anydesk installed'))
		self.readAD()
		self.notebook.ChangeSelection(2)
		
	def onBtnap (self,e): #deinstall anydesk
		self.logger.Clear()
		self.notebook.ChangeSelection(4)
		
		command = self.platform.admin+' apt purge anydesk -y'
		popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
		for line in popen.stdout:
			self.logger.WriteText(line)
			self.ShowStatusBarYELLOW(_('Deinstall, please wait... ')+line)
			self.logger.ShowPosition(self.logger.GetLastPosition())
		self.conf.set('MCS', 'anydesk', '0')
		self.ShowStatusBarGREEN(_('Anydesk uninstalled'))
		self.readAD()
		self.notebook.ChangeSelection(2)
		
	
	def onBtnas(self,e): #Anydesk starten
		subprocess.call(['pkill', '-f', 'anydesk'])
		subprocess.Popen('anydesk')
	
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
		
		
		#--------------------------------------------- functions-------------------------#
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

		self.printSensors()
		
	def read_asd (self) :
		stat_asd = self.conf.get('MCS', 'asd_state')
		if not stat_asd: stat_asd= "False"
		self.cbasd.SetValue(eval(stat_asd))

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

	def readMCS(self):
		value = self.conf.get('MCS', 'sending')
		if not value: value = '0'
		if value == '1': self.toolbar1.ToggleTool(103,True)
		else: self.toolbar1.ToggleTool(103,False)
	
	def readAD (self): # Anydesk Buttons
		value = self.conf.get('MCS', 'anydesk')
		if not value: value = '0'
		if value == "1": 
			self.btnai.Disable()
			self.btnap.Enable()
			self.btnas.Enable()
		else:
			self.btnai.Enable()
			self.btnap.Disable()
			self.btnas.Disable()
	
	def readwic (self): #read wic settings
		wic_state = self.conf.get('MCS', 'wic_state')
		if wic_state == 'True': self.widget_input_state.SetValue(True)
		
		wic1 = self.conf.get('MCS', 'wic1')
		if wic1:
			wic1 = list(wic1.split(","))
			self.widget_func1.SetValue(wic1[0])
			self.widget_signalkkey1.SetValue(wic1[1])
			self.widget_factor1.SetValue(wic1[2])
		
		wic2 = self.conf.get('MCS', 'wic2')
		if wic2 :
			wic2 = list(wic2.split(","))
			self.widget_func2.SetValue(wic2[0])
			self.widget_signalkkey2.SetValue(wic2[1])
			self.widget_factor2.SetValue(wic2[2])
		
		wic3 = self.conf.get('MCS', 'wic3')
		if wic3:
			wic3 = list(wic3.split(","))
			self.widget_func3.SetValue(wic3[0])
			self.widget_signalkkey3.SetValue(wic3[1])
			self.widget_factor3.SetValue(wic3[2])
		
		wic4 = self.conf.get('MCS', 'wic4')
		if wic3:
			wic4 = list(wic4.split(","))
			self.widget_func4.SetValue(wic4[0])
			self.widget_signalkkey4.SetValue(wic4[1])
			self.widget_factor4.SetValue(wic4[2])
				
		
	
	def OnToolSend(self,e):
		pass

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
		# sending data
		if self.toolbar1.GetToolState(103):
			self.conf.set('MCS', 'sending', '1')
			subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'enable'])
			self.ShowStatusBarGREEN(_('Sending data enabled'))
		else:
			self.conf.set('MCS', 'sending', '0')
			subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'disable'])
			self.ShowStatusBarYELLOW(_('Sending data disabled'))
		for i in self.ports.connections:
			self.conf.set('MCS', i['id'], str(i['port']))

		self.conf.set('MCS', 'owiresensors', str(self.config_osensors))
		
		# Autoshutdown
		if self.cbasd.IsChecked():
			subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'asdenable'])
			self.ShowStatusBarYELLOW(_('Autoshutdown enable'))
		else:
			subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'asddisable'])
			self.ShowStatusBarYELLOW(_('Autoshutdown disable'))
		
		self.conf.set('MCS', 'asd_state', str(self.cbasd.IsChecked()))
		
		self.readMCS()
		self.readConnections()
		self.printConnections()
		
		self.ShowStatusBarGREEN(_('Saved'))
		# Widget Input Config
		self.conf.set('MCS', 'wic_state', str(self.widget_input_state.IsChecked()))
		self.conf.set('MCS', 'wic1', str(self.widget_func1.GetValue()+","+self.widget_signalkkey1.GetValue()+","+self.widget_factor1.GetValue()))
		self.conf.set('MCS', 'wic2', str(self.widget_func2.GetValue()+","+self.widget_signalkkey2.GetValue()+","+self.widget_factor2.GetValue()))
		self.conf.set('MCS', 'wic3', str(self.widget_func3.GetValue()+","+self.widget_signalkkey3.GetValue()+","+self.widget_factor3.GetValue()))
		self.conf.set('MCS', 'wic4', str(self.widget_func4.GetValue()+","+self.widget_signalkkey4.GetValue()+","+self.widget_factor4.GetValue()))

	def OnToolCancel(self,e):
		self.ShowStatusBarRED(_('Changes canceled'))
		self.readMCS()
		self.readConnections()
		self.printConnections()
		self.read_sensors()
		self.read_asd()
		self.readwic()
	def OnToolOutput(self,e):
		self.logger.Clear()
		self.notebook.ChangeSelection(4)

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

################################################################################ edit Port

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

################################################################################ Add owire
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


################################################################################ Edit owire
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

################################################################################ Main

def main():
	try:
		platform2 = platform.Platform()
		if not platform2.postInstall(version,'mcs'):
			subprocess.Popen(['openplotterPostInstall', platform2.admin+' MCSPostInstall'])
			return
	except: pass

	app = wx.App()
	MyFrame().Show()
	app.MainLoop()

if __name__ == '__main__':
	main()
