# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 15:23:03 2023

@author: 1josh

This script is used to generate our emulator, run bayesian callibration, and create our corner plot.
"""

from surmise.emulation import emulator
from surmise.calibration import calibrator

import numpy as np
import scipy.stats as sps
import sys, os
import shutil
import subprocess
import pandas as pd

import corner
import matplotlib.pyplot as plt

import multiprocessing as mp
import time

# Returns dimensions of list of lists
def dim(a):
    if not type(a) == list:
        return []
    return [len(a)] + dim(a[0])

def count_directories(directory):
    count = 0
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            count += 1
    return count


class Prior:
    def lpdf(theta):
        ret = np.zeros(theta.shape[0])
        for i in range(len(paramMeans)):
            toAdd = sps.norm.logpdf(theta[:,i],paramMeans[i],paramStds[i])
            ret += toAdd
        return ret.reshape((-1,1))
    
    def rnd(n):
        ret = np.zeros((n,len(paramMeans)))
        for i in range(len(paramMeans)):
            ret[:,i] = sps.norm.rvs(loc=paramMeans[i],scale=paramStds[i],
                                    size=n)
        return ret


#%% Emulator Construction
# Main run code

#Parameters from Mao's paper
paramMeans = np.array([0.63,2.15,39.5,10.7,
                       0.64,2.06,42.1,11.1,
                       -8.309,-8.895,-9.425,-22.418])
paramStds = np.array([0.02,0.04,0.2,0.2,
                      0.02,0.04,0.4,0.5,
                      0.07,0.09,1.130,0.970])

# These specify the order of the nuclei of interest and their states
stateOrder = ['5He(3/2-_0)','5Li(3/2-_0)',
              '6Be(0+_0)','6Be(2+_0)',
              '6He(0+_0)','6He(2+_0)',
              '6Li(1+_0)','6Li(3+_0)',
              '6Li(0+_0)','6Li(2+_0)',
              '6Li(2+_1)','6Li(1+_1)']

# Experimental data from NNDC (it's S_n and NNDC Gamma error)
# The ordering is [E_0,Gamma_0,E_1,Gamma_1,...,E_n,Gamma_n]
minStdVal = 1E-6 # Since surmise can't handle anything less than this value, we pass it in as a minimum instead of 0
yMean = np.array([735.,600,1970.,1230,            # 5He, 5Li
                  1372.,92,3042.,1160,            # 6Be (0+, 2+)
                  -975.,minStdVal,822.,113,               # 6He (0+, 2+)
                  -3698.,minStdVal,-1512.,24,             # 6Li (1+_0 3+_0)
                  -135.1,8.2*10**-3,614,1.3*10**3, # 6Li (0+_0 2+_0)
                  1677.,541,1952,1.3*10**3])      # 6Li (2+_1 1+_1)
yStd = np.array([20,20,50,50,         # 5He, 5Li
                 9,6,50,60,           # 6Be (0+, 2+)
                 9,minStdVal,5,20,            # 6He (0+, 2+)
                 3,minStdVal,2,2,             # 6Li (1+_0 3+_0)
                 0.1,2*10**-3,22,100, # 6Li (0+_0 2+_0)
                 15,20,50,200])       # 6Li (2+_1 1+_1)


# For emulation
emuFolder = 'emulator-runs' # Folder to save the emulation data

originalDir = os.getcwd() # Get main directory this code runs in

emulatorDir = os.path.join(originalDir,emuFolder) # Identify emulation folder path

print('Building emulator...')
# Load high-fidelity model values and the corresponding theta values
modelVals = pd.read_csv(os.path.join(emulatorDir,"summary_model_vals.csv")).dropna(axis=1)
thetaData = pd.read_csv(os.path.join(emulatorDir,"summary_model_thetas.csv")).drop(['$GSM_NODES','$GSM_CPUS'],axis=1)

# We will want to make sure our GSM data is in the same format as our 
# experimental arrays to avoid errors, so we'll construct a new set of columns
newCols = []
for so in stateOrder:
    newCols.append('E'+so)
    newCols.append('G'+so)

# modelVals = modelVals.reindex(columns=newCols)
modelVals = modelVals[newCols]

print(modelVals)

# We need to convert everything to a numpy array
thetaTest = thetaData.to_numpy()
modelTest = modelVals.to_numpy()

xTest = np.arange(modelTest.shape[1]) #I don't really know what this does
print('x shape = ',xTest.shape,'yMean shape = ',yMean.shape,' theta shape = ',thetaTest.shape,' f shape = ',modelTest.shape)
emu = emulator(x=xTest,theta=thetaTest,f=modelTest,method='PCGP')
print('Done')

#%%

print(xTest.shape, thetaTest.shape)
emu.predict(xTest,thetaTest)

#%% Bayesian Calibration
print('Performing Bayesian Calibration...')
cal = calibrator(emu=emu,
                 y=yMean,
                 thetaprior=Prior,
                 yvar=yStd,
                 method='directbayes',
                 args={'theta0':paramMeans.reshape((1,-1)),
                       'sampler':'metropolis_hastings',
                       'numsamp':50000,
                       'burnSamples':2000,
                       'stepType':'normal'})
print('Done')

#%% Corner Plot
print('Making corner plot...')
myLabels = thetaData.columns
fig = corner.corner(cal.info['thetarnd'],
                    labels=myLabels)

axArr = np.array(fig.axes).reshape((len(paramMeans),len(paramMeans)))
for (i,theta) in enumerate(paramMeans):
    axArr[i,i].axvline(theta,color='red')
    axArr[i,i].axvspan(theta-paramStds[i],theta+paramStds[i],color='red',alpha=0.2)
    
    axArr[i,0].set(xlim=(0.5,0.7))

plt.savefig('corner_plot.png')
plt.savefig('corner_plot.pdf')
print('Done')
