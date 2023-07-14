# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 15:38:39 2023

@author: 1josh
"""
import numpy as np
import scipy.stats as sps
import os
import pandas as pd

#%%

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

# For reading and formatting data
def read_data(fileName_):
    '''
    given a file name, reads the file line-by-line saving each line as a string. List of strings contains all lines in file with each line being one element in the list.

    Returns list of lines.
    '''
    lines = []
    # Read data in (store each line as list called "lines")
    with open(fileName_) as fp:
        while True:
            line = fp.readline()
            
            lines.append(line)
            if not line: # End when at end of file (no more lines)
                break
    
    return lines


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

def setup_gsm(index,theta,templateDir_,emulatorDir_,templateNames_):
    # Create directory for current theta_i param set to put input folders in
    inputDir = os.path.join(emulatorDir_, str(index).zfill(6))
    os.makedirs(inputDir)

    # For all our input files given theta, set the proper parameters
    replaceDict = {"$GSM_NODES":mpiProcesses, "$GSM_CPUS":openMPthreads,
                    "$L1_dn":theta[0], "$L1_r0n":theta[1],
                    "$L1_v0n":theta[2], "$L1_vson":theta[3],
                    "$L1_dp":theta[4], "$L1_r0p":theta[5],
                    "$L1_v0p":theta[6], "$L1_vsop":theta[7],
                    "$Vc10":theta[8], "$Vc00":theta[9],
                    "$Vc01":theta[10], "$Vt10":theta[11]}

    # Loop through all templates in our templateNames list
    for tempName in templateNames_:
        # Open our template and read each line into a list
        with open(os.path.join(templateDir_,tempName)) as temp:
            fileTemplate = temp.readlines()
        
        # Create input file name by generic process template_5He_Mao2020
        inputName = tempName.replace('template','input')
        inputName = inputName.replace('.temp','.dat')
        
        # Open our input file as write
        with open(os.path.join(inputDir,inputName),'w') as f:
            # Loop through each input template line
            for line in fileTemplate:
                # loop through each dictionary item name 'key'
                for key, value in replaceDict.items():
                    # Replace the current dictionary item with its value
                    line = line.replace(key, str(value))
                f.write(line)
    return replaceDict


#%% Input params
# Main run code

#Parameters from Mao's paper
paramMeans = np.array([0.63,2.15,39.5,10.7,
                       0.64,2.06,42.1,11.1,
                       -8.309,-8.895,-9.425,-22.418])
paramStds = np.array([0.02,0.04,0.2,0.2,
                      0.02,0.04,0.4,0.5,
                      0.07,0.09,1.130,0.970])

# Names of all template files you wish to use 
# These specify the nuclei of interest and their states
templateNames = ['template_5He_Mao2020.temp','template_5Li_Mao2020.temp',
                  'template_6Be_Mao2020.temp','template_6He_Mao2020.temp',
                  'template_6Li_Mao2020.temp']

# Experimental data from NNDC (it's S_n and NNDC Gamma error)
# The ordering is [E_0,Gamma_0,E_1,Gamma_1,...,E_n,Gamma_n] 
yMean = np.array([735.,600,1970.,1230,            # 5He, 5Li
                  1372.,92,3042.,1160,            # 6Be (0+, 2+)
                  -975.,0,822.,113,               # 6He (0+, 2+)
                  -3698.,0,-1512.,24,             # 6Li (1+_0 3+_0)
                  -135.1,8.2*10**-3,614,1.3*10**3, # 6Li (0+_0 2+_0)
                  1677.,541,1952,1.3*10**3])      # 6Li (2+_1 1+_1)
minStdVal = 1E-6 # Since surmise can't handle anything less than this value, we pass it in as a minimum instead of 0
yStd = np.array([20,20,50,50,         # 5He, 5Li
                 9,6,50,60,           # 6Be (0+, 2+)
                 9,minStdVal,5,20,            # 6He (0+, 2+)
                 3,minStdVal,2,2,             # 6Li (1+_0 3+_0)
                 0.1,2*10**-3,22,100, # 6Li (0+_0 2+_0)
                 15,20,50,200])       # 6Li (2+_1 1+_1)

# GSM code information
# For parallelization
mpiProcesses = 4
openMPthreads = 8

nSamples = 200 # Total number of emulation dataset samples


emuFolder = 'emulator-runs' # Folder to save the emulation data
temFolder = 'templates' # Folder which contains the templates to build our input files

#%% Input file generation calls
originalDir = os.getcwd() # Get main directory this code runs in

emulatorDir = os.path.join(originalDir,emuFolder) # Identify emulation folder path
templateDir = os.path.join(originalDir,temFolder) # Identify template folder path

# Make emulator-runs folder if it doesn't exist
os.makedirs(emulatorDir,exist_ok=True)

# Get desired number of random theta values based on number of samples requested
thetaTest = Prior.rnd(nSamples)

modelThetas = [] # Stores each theta parameter set to be converted to dataframe when exporting to csv

for i, theta_ in enumerate(thetaTest):
    modelThetas.append(setup_gsm(i, theta_, templateDir, emulatorDir, templateNames))

# Likewise, we will take the theta dictionaries and save as a csv
modelThetas = pd.DataFrame(modelThetas)
modelThetas.to_csv(os.path.join(emulatorDir,"summary_model_thetas.csv"),index=False)





