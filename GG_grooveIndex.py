# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 09:48:44 2021

@author: olehe

DO NOT USE FOR ANYTHING
"""
import os
import numpy as np
import scipy.io
from scipy.stats.mstats import gmean


'''
test = np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
,[0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0]
,[1,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0]])

test = np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
,[0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0]
,[1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0]])
'''

testPattern = np.array([[1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
        1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
       [0, 0, 0, 0, 
		0, 1, 0, 0, 
		0, 0, 0, 0, 
		1, 0, 0, 0, 
		0, 0, 0, 0, 
		1, 0, 0, 0, 
		0, 0, 0, 0, 
		1, 0, 0, 0],
       [1, 0, 0, 0, 
		0, 0, 0, 0, 
		1, 0, 0, 0, 
		0, 0, 0, 0, 
		1, 0, 0, 0, 
		0, 0, 0, 0, 
		1, 0, 0, 0, 
		0, 0, 0, 0]])

snare = testPattern[1,]
kick = testPattern[2,]

def grooveIndex(patternA, patternB,events):

	#snare = test[1,]
	#kick = test[2,]
	snare = patternA
	kick = patternB
	
	
	
	# Load weights generated from PIPPET
	# These covers 2 seconds at 120 bpm (0 to 1.999)
	snareWeights = scipy.io.loadmat('snareWeighted.mat')['snareWeighted']
	kickWeights = scipy.io.loadmat('kickWeighted.mat')['kickWeighted']
	
	
	# fold patterns
	snareWeights = snareWeights[0]
	kickWeights = kickWeights[0]
	
	firstSnare = snare[0:16]
	secondSnare = snare[16:33]
	
	firstKick = kick[0:16]
	secondKick = kick[16:33]
	
	# Extract weights at relevant positions
	step = 0.001
	eventsPos = np.arange(0, 2, 0.125)/step
	eventsPos = eventsPos.astype(int)
	
	# just hardcoding in 0 at expected events just to check
	'''
	snareWeights[500] = 0
	snareWeights[1500] = 0
	kickWeights[0] = 0
	kickWeights[1000] = 0
	'''
	
	predsSnare = snareWeights[eventsPos[firstSnare==1]]
	predsKick = kickWeights[eventsPos[firstKick==1]]
	
	predsSnare = np.append(predsSnare, snareWeights[eventsPos[secondSnare==1]])
	predsKick = np.append(predsKick, kickWeights[eventsPos[secondKick==1]])
	# sum
	
	predsAll = np.concatenate((predsSnare, predsKick))
	
	#GI = sum(predsAll)/events
	#GI = np.median(predsAll)
	#GI = gmean(predsAll)
	GI = predsAll.mean()
	#GI = sum(predsAll)
	#a = predsAll/events
	#GI = a.mean()
	return GI




