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


test = np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
,[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]])

'''

def generate_midi(inputArray, tempo, loops, saveName):
	
	output = mido.MidiFile(type=1)
	# default is 480 ticks per beat.
	tickResolution = 480
	eventResolution = int(tickResolution / 4)
	tempoTicks = mido.bpm2tempo(tempo)
	
	
	# then write out from the input array
	# GM drums on channel 10 (9 0-indexed), keys 42 hihat 40 snare 36 kick
	# go for 40, 50 and 60 now
	instrKeys = [42, 40, 36]
	
	# so, its 480 ticks per beat (quarter note)
	
	# Just a track to set the tempo
	track = mido.MidiTrack()
	track.append(mido.MetaMessage('set_tempo', tempo=tempoTicks))
	track.append(mido.MetaMessage('end_of_track', time=(32 * tickResolution * loops)))
	
	output.tracks.append(track)
	
	# write one track per instrument
	
	
	count=0
	
	# hold-time for events
	# not implemented yet
	holdTime = int(tempoTicks/32)
	
	# generate tracks
	for key in instrKeys:
		track = mido.MidiTrack()
		
		thisInstr = inputArray[count,]
		count += 1
		previousEventTime = 0
		loopCount = 0
		for loop in range(0, loops):
			for n in range(0, 32):
				thisEventTime = n*tickResolution + (loopCount * tickResolution * 32)
				if thisInstr[n] == 1:
					# insert an event
					deltaTime = thisEventTime - previousEventTime
					track.append(mido.Message('note_on', note=key, velocity=100, channel=9, time=deltaTime))
					track.append(mido.Message('note_off', note=key, velocity=0, channel=9, time=0))
					
					
					previousEventTime = thisEventTime
				#else:
					#lastEventCount += tickResolution
			loopCount += 1
			#track.append(mido.MetaMessage('end_of_track', time=thisEventTime + tickResolution))
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