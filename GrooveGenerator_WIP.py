# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 16:21:53 2021

@author: olehe
"""


import sys
import os
import time
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import GGfunctions

# Note, make into 32 steps.



#%% Some global variables to start off with

stepNumbers = 32
bars = 2
stepChannels = 3

class GrooveGenerator(QWidget):
	
	def __init__(self):
		super().__init__()
		
		self.initUI()
		self.report_status('Ready.')

		
	
	
	def initUI(self):
		main_grid = QGridLayout()
		metro_grid = QGridLayout()
		top_grid = QGridLayout()
		
		statusLabel = QLabel('Status: ')
		top_grid.addWidget(statusLabel, 1, 1)
		self.statusBox = QLabel('Ready.')
		top_grid.addWidget(self.statusBox, 1, 2, 1, 3)

		
		main_grid.addLayout(top_grid, 1, 1, 1, 4)

		
		# grouping the pattern buttons
		self.metro_group = QButtonGroup()
		self.metro_group.setExclusive(False)
		# create the buttons
		# remember add a text field as well.
		instrLabels = ['Beat', 'Hihat', 'Snare', 'Kick']
		
		# also add some sort of bar at the top.
		# 2 bars x 16 events
		tickLabels = ['1.1', '', '', '', '1.2', '', '', '','1.3', '', '', '','1.4', '', '', '',
				'2.1', '', '', '', '2.2', '', '', '','2.3', '', '', '','2.4', '', '', '']
		
		count=0
		for i in range(0,stepChannels+1):
			thisLabel = QLabel(str(instrLabels[i]))
			metro_grid.addWidget(thisLabel, i, 0)
			for j in range(1,stepNumbers+1):
				if i == 0:
					thisLabel = QLabel(str(tickLabels[j-1]))
					metro_grid.addWidget(thisLabel, i, j)
				else:
					thisCheck = QCheckBox()
					thisCheck.clicked.connect(self.calculate)
					self.metro_group.addButton(thisCheck)
					self.metro_group.setId(thisCheck, count)
					metro_grid.addWidget(thisCheck,i,j)
					count+=1
		
		# insert into main grid
		main_grid.addLayout(metro_grid, 2, 1, 1, 4)
		
		runButton = QPushButton('Process pattern')
		runButton.clicked.connect(self.processPattern)
		main_grid.addWidget(runButton, 3, 4)
		
		calcButton = QPushButton('Calulate')
		calcButton.clicked.connect(self.calculate)
		main_grid.addWidget(calcButton, 3, 3)
		
		
		self.tempoField = QSpinBox()
		self.tempoField.setRange(30, 300)
		self.tempoField.setValue(120)
		main_grid.addWidget(self.tempoField, 3, 1)
		
		# loop selection buttons
		self.loopButton = QSpinBox()
		self.loopButton.setRange(1, 100)
		self.loopButton.setValue(1)
		main_grid.addWidget(self.loopButton, 3, 2)
		
		#self.outputName = QLineEdit('SaveName')
		#main_grid.addWidget(self.outputName, 4, 1, 1, 2)
		
		self.SIcalc = QLineEdit('SyncopationIndex')
		main_grid.addWidget(self.SIcalc, 4, 3, 1, 2)
		
		# hihat button
		
		hihatButton = QPushButton('Hihat')
		hihatButton.clicked.connect(self.hihat_on)
		main_grid.addWidget(hihatButton, 5, 1)
		
		kickButton = QPushButton('Kick')
		kickButton.clicked.connect(self.kick_on)
		main_grid.addWidget(kickButton, 5, 2)
		
		snareButton = QPushButton('Snare')
		snareButton.clicked.connect(self.snare_on)
		main_grid.addWidget(snareButton, 5, 3)
		
		clearButton = QPushButton('Reset')
		clearButton.clicked.connect(self.clear)
		main_grid.addWidget(clearButton, 5, 4)
		
		
		
		# save button
		saveButton = QPushButton('Save pattern')
		saveButton.clicked.connect(self.savePattern)
		main_grid.addWidget(saveButton, 6, 1)
		
		# load button
		loadButton = QPushButton('Load pattern')
		loadButton.clicked.connect(self.loadPattern)
		main_grid.addWidget(loadButton, 6, 2)
		
		# generate button
		generateButton = QPushButton('Generate pattern')
		generateButton.clicked.connect(self.generateRandomPattern)
		main_grid.addWidget(generateButton, 6, 3)
		
		# search pattern button
		searchButton = QPushButton('Search pattern')
		searchButton.clicked.connect(self.searchPattern)
		main_grid.addWidget(searchButton, 6, 4)
		
		
		self.setLayout(main_grid)
		self.setWindowTitle("GrooveGenerator")
		self.setGeometry(50,50,200,200)
		self.show()
	
	
	
	
	def getPattern(self):
		# gets the pattern as numpy array
		eventArray = []
		for n, button in enumerate(self.metro_group.buttons()):
			event = button.isChecked()
			eventArray.append(int(event))
		output_array = np.reshape(eventArray, (stepChannels, stepNumbers))
		
		return output_array
	
	
	def savePattern(self):
		pattern = self.getPattern()
		colNames = ['hihat', 'snare', 'kick']
		data = {'hihat':pattern[0,],
		  'snare':pattern[1,],
		  'kick':pattern[2,]}
		pattern_df = pd.DataFrame(data).T
		
		name = QFileDialog.getSaveFileName(self, 'Save File', filter='*.csv')
		print(name)
		if name[0][-4:] != '.csv':
			saveName = name[0] + '.csv'
		else:
			saveName = name[0]
		
		pattern_df.to_csv(saveName)
		self.report_status('Saved pattern')
		
		
		
	def loadPattern(self):
		# this is probably going to fail in many cases, since I don't care to write checks for weird formatting issues
		name = QFileDialog.getOpenFileName(self, 'Load File', filter='*.csv')
		
		try:
			pattern = pd.read_csv(name[0], index_col=0)
			#print(pattern)
			pattern_np = pattern.to_numpy().flatten()
			
			assert len(pattern_np) == stepNumbers * stepChannels
			
			for n, button in enumerate(self.metro_group.buttons()):
				button.setChecked(bool(pattern_np[n]))
			self.report_status('Loaded pattern')
		except:
			print('Loading file failed')
			self.report_status('Loading pattern failed')
			return
		
	def generateRandomPattern(self, verbose=True):
		# just a simple random pattern with some contraints
		
		maxEvents = 20
		minEvents = 4
		
		# set the hi-hat first
		hihat = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
		        1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
		
		# generate snare
		# need to bias towards not generating events it seems
		generate = True
		while generate:
			snare = np.random.randint(0, 1+1, 32)
			if sum(snare) >= minEvents and sum(snare) <= maxEvents:
				generate = False
				
		# generate kick
		# need to bias towards not generating events it seems
		generate = True
		while generate:
			kick = np.random.randint(0, 1+1, 32)
			if sum(kick) >= minEvents and sum(kick) <= maxEvents:
				generate = False
		
		pattern = np.array([hihat, snare, kick]).flatten()
		for n, button in enumerate(self.metro_group.buttons()):
			button.setChecked(bool(pattern[n]))
		if verbose:
			self.report_status('Generated pattern')
		return pattern
	
	def searchPattern(self):
		target, ok = QInputDialog.getDouble(self, 'Search for SI', 'Target SI:', 0.1, 0.0, 150.0, 3, Qt.WindowFlags(), 0.01)
		
		if not ok:
			return
		
		target = float(target)

		#target = 0.3
		generate = True
		waitTime = 60
		timeStart = time.time()
		self.report_status('Searching for pattern')
		count = 0
		while generate:
			count += 1
			thisPattern = self.generateRandomPattern(verbose=False)
			thisSI = self.calculate()
			
			if thisSI >= target*0.9 and thisSI <= target*1.1:
				generate = False
				self.report_status('Pattern found.')
			timeNow = time.time()
			if (timeNow-timeStart) > 10:
				generate=False
				self.report_status('Failed, tested ' + str(count) + ' patterns.')
			
			
			
	
	def calculate(self):
		# Calculates and reports the SI
		
		pattern = self.getPattern()
		patternA = pattern[1,] # snare
		patternB = pattern[2,] # kick
		
		SI = self.syncopationIndex(patternA, patternB)

		self.SIcalc.setText(str(round(SI,3)))
		
		#print('Syncopation Index is: ' + str(round(SI,3)))
		
		return SI
		
	def clear(self):
		print('Clearing.')
		for n, button in enumerate(self.metro_group.buttons()):
			button.setChecked(False)
			
			
	def hihat_on(self):
		print('Hihatting.')
		step=True
		for n, button in enumerate(self.metro_group.buttons()):			
			if n<32:
				if step:
					button.setChecked(True)
					step = False
				else:
					step = True
				
	def kick_on(self):
		print('kicking.')
		step = True
		count = 0
		for n, button in enumerate(self.metro_group.buttons()):
			if n>63:
				if step:
					button.setChecked(True)
					count = 0
					step = False
				else:
					count += 1
				if count > 2:
					step = True
					
	def snare_on(self):
		print('kicking.')
		step = False
		count = 0
		for n, button in enumerate(self.metro_group.buttons()):
			if n>32 and n<64:
				if step:
					button.setChecked(True)
					count = -4
					step = False
				else:
					count += 1
				if count > 2:
					step = True
			
	def report_status(self, status):
		self.statusBox.setText(status)
		print(status)
	
	def processPattern(self):
		self.report_status('Generating...')
		
		# get savename here
		text, ok = QInputDialog().getText(self, "Process",
                                     "Input name of pattern:", QLineEdit.Normal)
		if not ok:
			return
		text.replace(' ', '')
		
		
		output_array = self.getPattern()
		
		print(output_array)
		print(self.tempoField.text())
		tempo = int(self.tempoField.text())
		loops = int(self.loopButton.value())
		print('Doing ' + str(loops) + ' loops.')
		
		SI = self.calculate()
		SIstring = str(round(SI, 3))
		#replace comma with something?
		SIstring = SIstring.replace('.', '_')
		SIformatted = '-SI-' + SIstring
		
		
		#midiName = 'stimsMidi/' + self.outputName.text() + SIformatted + '.mid'
		#waveName = 'stimsWAV/' + self.outputName.text() + SIformatted + '.wav'
		
		midiName = 'stimsMidi/' + text + SIformatted + '.mid'
		waveName = 'stimsWAV/' + text + SIformatted + '.wav'
		

		GGfunctions.generate_midi(output_array, tempo, loops, midiName)
		GGfunctions.write_wav(midiName, waveName)
		self.report_status('Done! Ready.')

	
	def syncopationIndex(self, patternA, patternB):
		# always calculate for two repeats?
		# Maria's calculations are done for four repeats.
		def delta(m,n):
			if(m > n):
				return 1
			else:
				return 0
			
		def phi(a,w,i):
			j = i - 1
			if i >= 3 and a[i-1]== 0.0:
				j = i - 1 - delta(a[i-2],a[i-1])*delta(w[i-2],w[i-1])
			if i >= 5 and a[i-1]==0.0 and a[i-2]==0.0:
				j = i - 1 - 3*(delta(a[i-4],a[i-3])*delta(w[i-4],w[i-3])*delta(a[i-4],a[i-2])*delta(w[i-4],w[i-2])*delta(a[i-4],a[i-1])*delta(w[i-4],w[i-1]))
			return j
		
		def syncopation(s,b,w,B):
			c = 2.8 # optimized parameter that 'governs the relationship between metric weight'
			d = 1.6 # two-stream syncopation factor, equals d when both instruments are silent on i, otherwise 0
			h = 1.32 # scaling factor, chosen such that the slope of the linear link function (with perceived syncopation)
			n = len(w)
			S = 0
			for i in range(1,n): 
				j = phi(s,w,i)
				k = phi(b,w,i)
				S = S + (delta(w[i],w[k])*delta(b[k],b[i])*(c**(w[i])-c**(w[k]))
		              +delta(w[i],w[j])*delta(s[j],s[i])*(c**(w[i])-c**(w[j])))*d**(delta(1,s[i]+b[i]))
			return S/B*h
		
		# weights.
		w = (0, -3,-2, -3, -1, -3, -2, -3, -1, -3, -2, -3, -1,-3, -2, -3, 0, -3,-2, -3, -1, -3, -2, -3, -1, -3, -2, -3, -1,-3, -2, -3)
		
		SI = syncopation(patternA,patternB,w,32)

		return SI
		
  

if __name__ == '__main__':
	
	if not os.path.isdir('stimsMidi'):
		os.mkdir('stimsMidi')
	if not os.path.isdir('stimsWAV'):
		os.mkdir('stimsWAV')
	
	
	app = QApplication(sys.argv)
	test = GrooveGenerator()
	
	
	sys.exit(app.exec_())
