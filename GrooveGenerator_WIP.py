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
#import GG_grooveIndex

# some style

import qtmodern.styles
import qtmodern.windows

from pathlib import Path

root = Path()
if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
    qtmodern.styles._STYLESHEET = root / 'qtmodern/resources/style.qss'
    qtmodern.windows._FL_STYLESHEET = root / 'qtmodern/resources/frameless.qss'





# To add:
'''
Number of events, per instrument, or total? Go for total.
Maria's syncopation index, both at the same time.
Hoesl's SI = hSI
Maria's = wSI
Normalization of wav files?
'''



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
		
		#thanksLabel = QLabel('Heggli - 2021')
		#top_grid.addWidget(thanksLabel, 1, 6)

		
		main_grid.addLayout(top_grid, 1, 1, 1, 6)

		
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
		main_grid.addLayout(metro_grid, 2, 1, 1, 6)
		
		
		
	
		
		
		tempoLabel = QLabel('BPM:')
		main_grid.addWidget(tempoLabel, 3, 1)
		
		self.tempoField = QSpinBox()
		self.tempoField.setRange(30, 300)
		self.tempoField.setValue(120)
		main_grid.addWidget(self.tempoField, 3, 2)
		
		
		loopLabel = QLabel('Loops:')
		main_grid.addWidget(loopLabel, 3, 3)
		# loop selection buttons
		self.loopButton = QSpinBox()
		self.loopButton.setRange(1, 100)
		self.loopButton.setValue(1)
		main_grid.addWidget(self.loopButton, 3, 4)
		
		#self.outputName = QLineEdit('SaveName')
		#main_grid.addWidget(self.outputName, 4, 1, 1, 2)
		
		eventLabel = QLabel('nEvents:')
		main_grid.addWidget(eventLabel, 3, 5)
		
		self.eventCount = QLabel('')
		main_grid.addWidget(self.eventCount, 3, 6)
		
		# hihat button
		
		insertFillLabel = QLabel('Autofill:')
		main_grid.addWidget(insertFillLabel, 4, 1)
		
		hihatButton = QPushButton('Hihat')
		hihatButton.clicked.connect(self.hihat_on)
		main_grid.addWidget(hihatButton, 4, 2)
		
		kickButton = QPushButton('Kick')
		kickButton.clicked.connect(self.kick_on)
		main_grid.addWidget(kickButton, 4, 3)
		
		snareButton = QPushButton('Snare')
		snareButton.clicked.connect(self.snare_on)
		main_grid.addWidget(snareButton, 4, 4)
		
		clearButton = QPushButton('Reset')
		clearButton.clicked.connect(self.clear)
		main_grid.addWidget(clearButton, 4, 5)
		
		
		
		
		
		# load button
		loadButton = QPushButton('Load pattern')
		loadButton.clicked.connect(self.loadPattern)
		main_grid.addWidget(loadButton, 5, 1)
		
		# save button
		saveButton = QPushButton('Save pattern')
		saveButton.clicked.connect(self.savePattern)
		main_grid.addWidget(saveButton, 5, 2)
		
		SIlabelH = QLabel('Hoesl\'s SI:')
		main_grid.addWidget(SIlabelH, 5, 3)
		self.SIcalcH = QLabel('N/A')
		main_grid.addWidget(self.SIcalcH, 5, 4)
		SIlabelW = QLabel('Witek\'s SI:')
		main_grid.addWidget(SIlabelW, 5, 5)
		self.SIcalcW = QLabel('N/A')
		main_grid.addWidget(self.SIcalcW, 5, 6)
		
		
		
		# generate button
		generateButton = QPushButton('Generate pattern')
		generateButton.clicked.connect(self.generateRandomPattern)
		main_grid.addWidget(generateButton, 6, 1)
		
		# search pattern button
		searchButton = QPushButton('Search pattern')
		searchButton.clicked.connect(self.searchPattern)
		main_grid.addWidget(searchButton, 6, 2)
		
		calcButton = QPushButton('Recalculate SI')
		calcButton.clicked.connect(self.calculate)
		main_grid.addWidget(calcButton, 6, 3)
		
		# process pattern
		runButton = QPushButton('Process pattern')
		runButton.clicked.connect(self.processPattern)
		main_grid.addWidget(runButton, 6, 5, 1, 2)
		
		
		self.setLayout(main_grid)
		self.setWindowTitle("Groove Generator")
		self.setGeometry(50,50,200,200)
		self.setWindowIcon(QIcon('icon.ico'))
		#self.show()
	
	
	
	
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
		
		patternA = pattern[1,] # snare
		patternB = pattern[2,] # kick
		
		output = self.syncopationIndexHoesl(patternA, patternB)
		hWeights = output[1]
		output = self.syncopationIndexWitek(patternA, patternB)
		wWeights = output[1]
		
		
		
		
		
		colNames = ['hihat', 'snare', 'kick', 'hWeights', 'wWeights']
		data = {'hihat':pattern[0,],
		  'snare':pattern[1,],
		  'kick':pattern[2,],
		  'hWeights':hWeights,
		  'wWeights':wWeights}
		pattern_df = pd.DataFrame(data).T
		
		name = QFileDialog.getSaveFileName(self, 'Save File', filter='*.csv')
		#print(name)
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
			pattern_np = pattern.to_numpy()
			pattern_np = pattern_np[0:3,].flatten()
			
			assert len(pattern_np) == stepNumbers * stepChannels
			
			for n, button in enumerate(self.metro_group.buttons()):
				button.setChecked(bool(pattern_np[n]))
			self.report_status('Loaded pattern')
			self.calculate()
		except:
			#print('Loading file failed')
			self.report_status('Loading pattern failed')
			return
	
	def countEvents(self, hihats=False):
		pattern = self.getPattern()
		
		if hihats:
			events = sum(pattern.flatten())
			#print(events)
		else:
			snares = pattern[1,]
			kicks = pattern[2,]
			both = np.array([snares, kicks]).flatten()
			events = sum(both)
		
		
		return events
	
	
	def generateRandomPattern(self, verbose=True):
		# just a simple random pattern with some contraints
		
		maxEvents = 20
		minEvents = 10
		# collapse over both instruments? Total between 12 and 18?
		
		# set the hi-hat first
		hihat = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
		        1, 0, 1, 0, 1, 0, 1, 0, 1, 0])

		# now generating them both together
		generate = True
		while generate:
			#snare = np.random.randint(0, 1+1, 32)
			snare = np.round(1-np.random.power(1,32)).astype(int)
			kick = np.round(1-np.random.power(1,32)).astype(int)
			both = np.array([snare, kick]).flatten()
			if sum(both) >= minEvents and sum(both) <= maxEvents:
				generate = False
		
		pattern = np.array([hihat, snare, kick]).flatten()
		for n, button in enumerate(self.metro_group.buttons()):
			button.setChecked(bool(pattern[n]))
		
		
		if verbose:
			self.report_status('Generated pattern')
		self.calculate()
		return pattern
	
	def searchPattern(self):
		self.report_status('Searching for pattern')
		
		# first get which measure
		measure, ok = QInputDialog.getItem(self, 'Select', 'Select SI measure:', ['Hoesl\'s', 'Witek\'s'], 0, False)
		
		if not ok:
			return
		
		if measure == 'Hoesl\'s':
			defaultValue = 0.1
			minValue = 0.0
			maxValue = 150.0
			decimals = 3
			steps = 0.01
			select = 0
		elif measure == 'Witek\'s':
			defaultValue = 10.0
			minValue = 0.0
			maxValue = 150.0
			decimals = 1
			steps = 0.05
			select = 1
		
		
		
		
		target, ok = QInputDialog.getDouble(self, 'Search for SI', 'Target SI:', defaultValue, minValue, maxValue, decimals, Qt.WindowFlags(), steps)
		
		if not ok:
			return
		
		target = float(target)

		#target = 0.3
		generate = True
		waitTime = 60
		timeStart = time.time()
		
		count = 0
		while generate:
			count += 1
			thisPattern = self.generateRandomPattern(verbose=False)
			SIs = self.calculate()
			thisSI = SIs[select]
			
			if thisSI >= target*0.9 and thisSI <= target*1.1:
				generate = False
				self.report_status('Pattern found.')
			timeNow = time.time()
			if (timeNow-timeStart) > 10:
				generate=False
				self.report_status('Failed, tested ' + str(count) + ' patterns.')
			
			
			
	
	def calculate(self, verbose=True):
		# Calculates and reports the SI
		
		pattern = self.getPattern()
		patternA = pattern[1,] # snare
		patternB = pattern[2,] # kick
		
		output = self.syncopationIndexHoesl(patternA, patternB)
		hSI = output[0]
		output = self.syncopationIndexWitek(patternA, patternB)
		wSI = output[0]

		self.SIcalcH.setText(str(round(hSI,3)))
		self.SIcalcW.setText(str(round(wSI,3)))
		
		events = self.countEvents()
		self.eventCount.setText(str(events))
		
		#print('Syncopation Index is: ' + str(round(SI,3)))
		
		#GI = GG_grooveIndex.grooveIndex(patternA, patternB, events)
		#print(GI)
		#print(GI)
		
		return hSI, wSI#, GI
		
	def clear(self):
		#print('Clearing.')
		for n, button in enumerate(self.metro_group.buttons()):
			button.setChecked(False)
			
			
	def hihat_on(self):
		#print('Hihatting.')
		step=True
		for n, button in enumerate(self.metro_group.buttons()):			
			if n<32:
				if step:
					button.setChecked(True)
					step = False
				else:
					step = True
				
	def kick_on(self):
		#print('kicking.')
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
		#print('kicking.')
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
		#print(status)
	
	def processPattern(self):
		self.report_status('Generating...')
		
		# get savename here
		text, ok = QInputDialog().getText(self, "Process",
                                     "Input name of pattern:", QLineEdit.Normal)
		if not ok:
			return
		text.replace(' ', '')
		
		
		output_array = self.getPattern()
		
		#print(output_array)
		#print(self.tempoField.text())
		tempo = int(self.tempoField.text())
		loops = int(self.loopButton.value())
		print('Doing ' + str(loops) + ' loops.')
		
		SI = self.calculate()
		hSI = SI[0]
		wSI = SI[1]
		hSIstring = str(round(hSI, 3))
		wSIstring = str(round(wSI, 3))
		#replace comma with something?
		hSIstring = hSIstring.replace('.', '_')
		hSIformatted = '-hSI-' +hSIstring
		
		wSIstring = wSIstring.replace('.', '_')
		wSIformatted = '-wSI-' +wSIstring
		
		
		#midiName = 'stimsMidi/' + self.outputName.text() + SIformatted + '.mid'
		#waveName = 'stimsWAV/' + self.outputName.text() + SIformatted + '.wav'
		
		midiName = 'stimsMidi/' + text + hSIformatted + wSIformatted + '.mid'
		waveName = 'stimsWAV/' + text + hSIformatted + wSIformatted + '.wav'
		

		GGfunctions.generate_midi(output_array, tempo, loops, midiName)
		GGfunctions.write_wav(midiName, waveName)
		self.report_status('Done! Ready.')

	
	def syncopationIndexHoesl(self, patternA, patternB):
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
			w_out = np.zeros(32, dtype = float)
			c = 2.8 # optimized parameter that 'governs the relationship between metric weight'
			d = 1.6 # two-stream syncopation factor, equals d when both instruments are silent on i, otherwise 0
			h = 1.32 # scaling factor, chosen such that the slope of the linear link function (with perceived syncopation)
			n = len(w)
			S = 0
			for i in range(1,n): 
				j = phi(s,w,i)
				k = phi(b,w,i)
				w_out[i] = (delta(w[i],w[k])*delta(b[k],b[i])*(c**(w[i])-c**(w[k]))
              +delta(w[i],w[j])*delta(s[j],s[i])*(c**(w[i])-c**(w[j])))*d**(delta(1,s[i]+b[i]))
			
			S = sum(w_out)
			return S/B*h, w_out
		
		# weights.
		w = (0, -3,-2, -3, -1, -3, -2, -3, -1, -3, -2, -3, -1,-3, -2, -3, 0, -3,-2, -3, -1, -3, -2, -3, -1, -3, -2, -3, -1,-3, -2, -3)
		
		output = syncopation(patternA,patternB,w,32)
		

		return output
	
	
	def syncopationIndexWitek(self, patternA, patternB):
		# weights.
		w = (0, -3,-2, -3, -1, -3, -2, -3, -1, -3, -2, -3, -1,-3, -2, -3, 0, -3,-2, -3, -1, -3, -2, -3, -1, -3, -2, -3, -1,-3, -2, -3)
		
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
		
		def syncopation(patternA, patternB, w, B):
			w_out = np.zeros(32, dtype=int)
			n = len(w)
			S = 0
			for i in range(1,n):
				j = phi(patternA, w, i)
				k = phi(patternB, w, i)
				Swb = delta(w[i],w[k])*delta(patternB[k],patternB[i])
				Sws = delta(w[i],w[j])*delta(patternA[j],patternA[i])
				Swb1 = delta(1, Swb)
				Wb = w[i] - w[k] + 2 + 3*delta(1,patternA[i]+patternB[i])
				Ws = w[i] - w[j] + 1 + 4*delta(1,patternA[i]+patternB[i])
				
				w_out[i] = Swb*Wb + Sws*Ws*Swb1
			S = sum(w_out)
			return S, w_out
		
		output = syncopation(patternA, patternB, w, 32)
		
		
		return output
		
  

if __name__ == '__main__':
	
	if not os.path.isdir('stimsMidi'):
		os.mkdir('stimsMidi')
	if not os.path.isdir('stimsWAV'):
		os.mkdir('stimsWAV')
	
	
	app = QApplication(sys.argv)
	qtmodern.styles.dark(app)

	window = GrooveGenerator()
	mw = qtmodern.windows.ModernWindow(window)
	mw.show()
	
	
	sys.exit(app.exec_())
