# -*- coding: utf-8 -*-
"""
Created on Mon Oct 11 13:59:46 2021

@author: olehe
"""
import mido
import os
import glob
#import math
#from scipy.io import wavfile
import subprocess
import time
#import random
#import numpy as np
#import pandas as pd
import sys
'''
test = np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
,[0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0]
,[1,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0]])
'''

def generate_midi(inputArray, tempo, saveName):
	
	output = mido.MidiFile(type=1)
	# default is 480 ticks per beat.
	tempoTicks = mido.bpm2tempo(tempo)
	
	
	# then write out from the input array
	# find the midi channels for shit, and keys for sounds
	# go for 40, 50 and 60 now
	instrKeys = [42, 40, 36]
	
	# so, its 480 ticks per beat (quarter note)
	
	#one track per!!!
	track = mido.MidiTrack()
	track.append(mido.MetaMessage('set_tempo', tempo=tempoTicks))
	output.tracks.append(track)
	
	tickResolution = 480
	count=0
	for key in instrKeys:
		track = mido.MidiTrack()
		#track.append(mido.MetaMessage('set_tempo', tempo=tempoTicks))
		thisInstr = inputArray[count,]
		count += 1
		lastEventCount = 0
		previousEventTime = 0
		for n in range(0, 16):
			thisEventTime = n*tickResolution
			if thisInstr[n] == 1:
				# insert an event
				deltaTime = thisEventTime - previousEventTime
				track.append(mido.Message('note_on', note=key, velocity=100, channel=9, time=deltaTime))
				#track.append(mido.Message('note_on', note=key, velocity=100, channel=9, time=n*tickResolution))
				#track.append(mido.Message('note_off', note=key, velocity=100, channel=9, time=int(tickResolution/16)))
				track.append(mido.Message('note_off', note=key, velocity=100, channel=9, time=0))
				previousEventTime = thisEventTime
				#lastEventCount = 0
			else:
				lastEventCount += tickResolution
		
		track.append(mido.MetaMessage('end_of_track', time=thisEventTime + tickResolution))
		output.tracks.append(track)		
			
	
	output.save(saveName)
	
	
	return


def write_wav(midiName, name):
	#REPLACE THIS WITH YOUR OWN FLUIDSYNTH
	fluidsynth = 'C:/Users/olehe/Documents/GitHub/SanderGenerator/fluidsynth-2.2.2/bin/fluidsynth.exe'
	result = subprocess.run([fluidsynth, "-i", "-q", "default.sf2", midiName, "-T", "wav", "-F", name], shell=True)
	# This doesn't always play nice, but it's solved by simply letting it sleep a bit.
	# I've not tested without the sleep, so it could possible work without it.
	time.sleep(1)
	
	return