# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 16:21:53 2021

@author: olehe
"""


import sys
import os
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import GGfunctions



#%% Some global variables to start off with

stepNumbers = 16
stepChannels = 3

class StepSequenceInput(QWidget):
	
	def __init__(self):
		super().__init__()
		
		self.initUI()
		self.report_status('Ready.')
		#self.getPattern()
		
	
	
	def initUI(self):
		main_grid = QGridLayout()
		metro_grid = QGridLayout()
		
		self.metro_group = QButtonGroup()
		self.metro_group.setExclusive(False)
		# create the buttons
		# remember add a text field as well.
		instrLabels = ['Beat', 'hihat', 'snare', 'kick']
		
		# also add some sort of bar at the top.
		# lock it at 16?
		tickLabels = ['1', '', '1.2', '', '2', '', '2.2', '','3', '', '3.2', '','4', '', '4.2', '']
		
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
					self.metro_group.addButton(thisCheck)
					self.metro_group.setId(thisCheck, count)
					metro_grid.addWidget(thisCheck,i,j)
					count+=1
		
		# insert into main grid
		main_grid.addLayout(metro_grid, 1, 1, 1, 4)
		
		runButton = QPushButton('Run')
		runButton.clicked.connect(self.getPattern)
		main_grid.addWidget(runButton, 2, 4)
		
		calcButton = QPushButton('Calulate')
		calcButton.clicked.connect(self.calculate)
		main_grid.addWidget(calcButton, 2, 3)
		
		self.tempoField = QLineEdit('120')
		main_grid.addWidget(self.tempoField, 2, 1)
		
		self.outputName = QLineEdit('SaveName')
		main_grid.addWidget(self.outputName, 3, 1, 1, 2)
		
		self.SIcalc = QLineEdit('SyncopationIndex')
		main_grid.addWidget(self.SIcalc, 3, 3, 1, 2)
		
		# hihat button
		
		hihatButton = QPushButton('Hihat')
		hihatButton.clicked.connect(self.hihat_on)
		main_grid.addWidget(hihatButton, 4, 1)
		
		kickButton = QPushButton('Kick')
		kickButton.clicked.connect(self.kick_on)
		main_grid.addWidget(kickButton, 4, 2)
		
		clearButton = QPushButton('Reset')
		clearButton.clicked.connect(self.clear)
		main_grid.addWidget(clearButton, 4, 4)
		
		# loop selection buttons
		self.loopButton = QSpinBox()
		self.loopButton.setRange(1, 100)
		self.loopButton.setValue(1)
		main_grid.addWidget(self.loopButton, 2, 2)
		
		
		
		
		self.setLayout(main_grid)
		self.setWindowTitle("GrooveGenerator")
		self.setGeometry(50,50,200,200)
		self.show()
	
	def calculate(self):
		self.SIcalc.setText('Not implemented')
		print('Will eventually calculate shit')
		
	def clear(self):
		print('Clearing.')
		for n, button in enumerate(self.metro_group.buttons()):
			button.setChecked(False)
			
	def hihat_on(self):
		print('Hihatting.')
		for n, button in enumerate(self.metro_group.buttons()):
			if n<16:
				button.setChecked(True)
				
	def kick_on(self):
		print('kicking.')
		for n, button in enumerate(self.metro_group.buttons()):
			if n>31:
				button.setChecked(True)
			
	def report_status(self, status):
		print(status)
	
	def getPattern(self):
		self.report_status('Generating...')
		pattern = np.zeros((3,8))
		
		count=0
		eventArray = []
		for n, button in enumerate(self.metro_group.buttons()):
			event = button.isChecked()
			eventArray.append(int(event))
		
		
		'''
		for i in range(0, stepChannels):
			for j in range(0,stepNumbers):
				event = self.metro_group.buttons(count).isChecked()
				pattern[i,j] = event
				count+=1
		'''
		
		output_array = np.reshape(eventArray, (stepChannels, stepNumbers))
		print(output_array)
		print(self.tempoField.text())
		tempo = int(self.tempoField.text())
		loops = int(self.loopButton.value())
		
		midiName = 'stimsMidi/' + self.outputName.text() + '.mid'
		waveName = 'stimsWAV/' + self.outputName.text() + '.wav'
		
		#loops = 2
		
		GGfunctions.generate_midi(output_array, tempo, loops, midiName)
		GGfunctions.write_wav(midiName, waveName)
		self.report_status('Done! Ready.')

	
	
	
	


if __name__ == '__main__':
	
	if not os.path.isdir('stimsMidi'):
		os.mkdir('stimsMidi')
	if not os.path.isdir('stimsWAV'):
		os.mkdir('stimsWAV')
	
	
	app = QApplication(sys.argv)
	test = StepSequenceInput()
	
	
	sys.exit(app.exec_())
