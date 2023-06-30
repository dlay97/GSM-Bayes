import os, shutil, re

#%% Saving last-saved iteration (-ish)
reString = "\d{1,4}(L|B)"

lastIter = 0
thooutFiles = [f for f in os.listdir() if not os.path.isdir(f) and f.startswith("thoout")]
for thoFile in thooutFiles: 
    with open(thoFile,"r",errors="ignore") as f:
        lines = f.readlines()

    keptLine = ""

    for l in lines:
        if re.search(reString,l):
            keptLine = l

    if keptLine:
        lastIterSingleFile = int(re.search(reString,keptLine)[0].rstrip("B").rstrip("L"))
    else:
        lastIterSingleFile = 0

    lastIterSaved = 20*(lastIterSingleFile//20)
    lastIter = max(lastIter,lastIterSaved)

if os.path.isfile("lastIter.txt"):
    with open("lastIter.txt","r") as f:
        previousIter = int(f.readline().replace("\n",""))
else:   
    previousIter = 0

with open("lastIter.txt","w") as f:
    f.writelines([str(lastIter+previousIter)])

#%% Saving old thoout files
oldSaveDirs = [f for f in os.listdir() if os.path.isdir(f) and f.startswith("previous_thoout")]

if len(thooutFiles) > 0:
    saveDir = "previous_thoout_"+str(len(oldSaveDirs)+1).zfill(3)
    os.mkdir(saveDir)
    for f in thooutFiles:
        shutil.move(f,saveDir)

#%% Updating hfbtho_NAMELIST.dat
with open("lastIter.txt","r") as f:
    iterReached = int(f.readline().replace("\n",""))

with open("hfbtho_NAMELIST_template.dat","r") as fIn:
    linesIn = fIn.readlines()

newMaxIters = 1000-iterReached
if newMaxIters < 0:
    newMaxIters = 0
linesOut = []
for l in linesIn:
    linesOut.append(l.replace("$nIters",str(newMaxIters)))

with open("hfbtho_NAMELIST.dat","w") as fOut:
    fOut.writelines(linesOut)
        

