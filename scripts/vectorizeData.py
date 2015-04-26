# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 20:00:28 2014

@author: tgunter
"""

from ctypes import *
from ctypes.wintypes import *
import struct
import win32gui
import win32process
import win32api
import os

OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle
GetModuleInformation = windll.psapi.GetModuleInformation
FindWindow = win32gui.FindWindow

#typedef struct Moduleinfo
class MODULEINFO(Structure):
    _fields_ = [
        ("lpBaseOfDll",     c_void_p),    # remote pointer
        ("SizeOfImage",     c_uint),    #Size
        ("EntryPoint",      c_void_p),    # remote pointer
]


def moveTest(move):
    moves = [64, 128, 256, 448, 512, 1024, 2048, 3584, 576, 1152, 2304, 192, 320, 384, 1536, 2560, 3072]
    for i in moves:
        for n in range(0,7):
            if i+4*n == move:
                return True
            if n < 6 :
                if i+4*n+2 == move :
                    
                    return True
    return False
def directionTest(direction):
    direc = [0, 2, 4, 8, 10, 12,16,18,20]
    for i in direc:
        if i == direction:
            return True            

    return False 
##################
#Finds the index of the first instance of an element with in a subset of a list if not there reurns length of list
def FindFirstIndex(elementOff, listA, indexValue):
    if indexValue in listA[elementOff:]:
        return listA[elementOff:].index(indexValue) + elementOff

    return len(listA)

def FormatError(fileName):
    print fileName, "improperly formatted."

#####################
# 
def ReadMemoryInt(processHandle, baseAddr, offSets, addrShift = -1):
    uniqString = ""
    for l in offSets:
        uniqString = uniqString+l
    #print offSets[0], " offsets"
    bufferA = c_char_p(b"The data goes here..." + str(uniqString) + " " +str(addrShift))   #This buffer string must be unique or ReadMem will return the same value
    bufferSize = len(bufferA.value)
    bytesRead = c_ulong(0)
    val = c_int()
    address = 0
    #print bufferA
    
    
    if addrShift != -1:
        #print addrShift, " addrShift"
        testing = str(hex(int(offSets[-1], 16) + addrShift))

    
    for i in offSets:
        if(address == 0) :
            address = baseAddr + int(i, 16)
            if (i == offSets[-1] and addrShift !=-1):
                address = baseAddr + int(testing,16)
        else:
            address = val.value + int(i, 16)
        ReadProcessMemory(processHandle, address , bufferA, bufferSize, byref(bytesRead))
        memmove(byref(val), bufferA, sizeof(val))   #looks in bufferA and returns a string value held inside
        
        if i == offSets[-1]:
            bufferA = None  #Precaution may not be necessary
            del bufferA     #Precaution may not be necessary
            return val.value
    bufferA = None
    del bufferA
    return 0

#
def ReadMemoryFl(processHandle, baseAddr, offSets, addrShift = -1):
    uniqString = ""
    for l in offSets:
        uniqString = uniqString + l
    
    bufferA = c_char_p(b"The data goes here..."+uniqString)
    bufferSize = len(bufferA.value)
    bytesRead = c_ulong(0)
    valAddr = c_int()
    val = c_float()
    address = 0
    
    for i in offSets:
        if(address == 0) :
            address = baseAddr + int(i, 16)
        else:
            address = valAddr.value + int(i, 16)
        ReadProcessMemory(processHandle, address , bufferA, bufferSize, byref(bytesRead))
        memmove(byref(val), bufferA, sizeof(val))
        memmove(byref(valAddr), bufferA, sizeof(valAddr))

        if i == offSets[-1]:
            bufferA=None
            del bufferA
            return val.value
    bufferA = None
    del bufferA
    return 0

def ReadMemoryChoose(readDic, processHandle, baseAddr, addrShift = -1):
    if readDic["type"] == "int":
        return ReadMemoryInt(processHandle, baseAddr, readDic["offSets"], addrShift)
    elif readDic["type"] == "float":
        return ReadMemoryFl(processHandle, baseAddr, readDic["offSets"], addrShift)
    else:
        return-1
    return -1
###########################
#f_type.strip("\n"), f_offSets, p_type.strip("\n"), p_offSets
def ReadGameName():
    
    GameName = "GameName.txt"
    f = open(GameName, "r")
    lines = f.readlines()
    if "Window Name:\n" in lines: 
        i=lines.index("Window Name:\n")
        windowName = lines[i+1]
    else: 
        FormatError(GameName)
        return -1
    if "Exe Name:\n" in lines:
        i = lines.index("Exe Name:\n")
        exeName = lines[i+1]
    else: 
        FormatError(GameName)
        return -1
    
    f.close()
    return windowName.strip("\n"), exeName.strip("\n")
    
def ReadGlobal():
    Global = "Global.txt"
    f = open(Global, "r")
    lines = f.readlines()
    if "Frames:\n" in lines:
        i = lines.index("Frames:\n")
        f_type = lines[i+1].strip("\n")
        f_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Global)
        return -1
    if "Paused:\n" in lines:
        i = lines.index("Paused:\n")
        p_type = lines[i+1].strip("\n")
        p_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Global)
        return -1

    if "HasMatchEnded:\n" in lines:
        i = lines.index("HasMatchEnded:\n")
        hme_type = lines[i+1].strip("\n")
        hme_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Global)
        return -1

    f.close()
    globalFrames = {"type":f_type, "offSets":f_offSets}
    globalPause = {"type":p_type, "offSets":p_offSets}
    globalHME = {"type":hme_type, "offSets":hme_offSets}
    return globalFrames, globalPause, globalHME


def ReadPlayer(pNumber):
    Player = "Player"+str(pNumber)+".txt"
    f = open(Player, "r")
    lines = f.readlines()
    if "Character:\n" in lines:
        i = lines.index("Character:\n")
        ch_type = lines[i+1].strip("\n")
        ch_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Player+" ch ")
        return -1
    if "Percent Health:\n" in lines:
        i = lines.index("Percent Health:\n")
        h_type = lines[i+1].strip("\n")
        h_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Player+" h ")
        return -1
    if "Ultra Meter:\n" in lines:
        i = lines.index("Ultra Meter:\n")
        u_type = lines[i+1].strip("\n")
        u_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Player+" u ")
        return -1
    if "Super Meter:\n" in lines:
        i = lines.index("Super Meter:\n")
        s_type = lines[i+1].strip("\n")
        s_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Player+" s ")
        return -1
    if "Position X:\n" in lines:
        i = lines.index("Position X:\n")
        px_type = lines[i+1].strip("\n")
        px_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Player+" px ")
        return -1
    if "Position Y:\n" in lines:
        i = lines.index("Position Y:\n")
        py_type = lines[i+1].strip("\n")
        py_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Player+" py ")
        return -1
    if "Movement State:\n" in lines:
        i = lines.index("Movement State:\n")
        ms_type = lines[i+1].strip("\n")
        ms_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Player+" ms ")
        return -1
    if "Number of Buttons:\n" in lines:
        i = lines.index("Number of Buttons:\n")
        nb_type = lines[i+1].strip("\n")
        nb_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Player+" b ")
        return -1
    if "Frames Since:\n" in lines:
        i = lines.index("Frames Since:\n")
        fs_type = lines[i+1].strip("\n")
        fs_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Player+" fs ")
    if "Button Pressed:\n" in lines:
        i = lines.index("Button Pressed:\n")
        bp_type = lines[i+1].strip("\n")
        bp_offSets = [lines[n].strip("\n") for n in range(i+2,FindFirstIndex(i+1, lines, "\n"))]
    else:
        FormatError(Player+" fs ")

    f.close()
    
    character = {"type":ch_type, "offSets":ch_offSets}
    health = {"type":h_type, "offSets":h_offSets}
    ultra = {"type":u_type, "offSets":u_offSets}
    special = {"type":s_type, "offSets":s_offSets}
    positionX = {"type":px_type, "offSets":px_offSets}
    positionY = {"type":py_type, "offSets":py_offSets}
    moveState = {"type":ms_type, "offSets":ms_offSets}
    numberButton = {"type":nb_type, "offSets":nb_offSets}
    frameSince = {"type":fs_type, "offSets":fs_offSets}
    buttonPressed = {"type":bp_type, "offSets":bp_offSets}
    
    return character, health, ultra, special, positionX, positionY, moveState, numberButton, frameSince, buttonPressed
##########################
#Create data file
def createTrainingFile(processHandle, moduleHandle, characterName, playerName, matchNumber=0):
    fileName = playerName +"_" +characterName + "_" + str(matchNumber)
    absPath = os.path.abspath("Training/%s.txt" % fileName)
    f = open(absPath, "w")

    globalFrames, globalPause, globalHME = ReadGlobal()
    character1, health1, ultra1, special1, positionX1, positionY1, moveState1, numberButton1, frameSince1, buttonPressed1 = ReadPlayer(1)
    character2, health2, ultra2, special2, positionX2, positionY2, moveState2, numberButton2, frameSince2, buttonPressed2 = ReadPlayer(2)    
    
#ButtonPressed, DirectionPressed, ||    Player1[...], Player2[...]
#[...] = char, health, u, s, posx, posy, mvState, frames in mvState, butPressed[16], framesSince[16]
    i = 0
    mvState1 = 0
    mvState2 = 0
    framesInMvState1 = 0
    framesInMvState2 = 0
    nButtons = 0
    classification = 0
    directionMV = 0
    fSince = []
    saveString = ""
    newButtonPressed = 0
    
    print "Running..."
    while (ReadMemoryChoose(globalHME, processHandle, moduleHandle) != 1) and ReadMemoryChoose(globalPause, processHandle, moduleHandle) != 1 :
        
        frames = ReadMemoryChoose(globalFrames, processHandle, moduleHandle)

        if(frames+1 ==  ReadMemoryChoose(globalFrames, processHandle, moduleHandle)):
        #

            if nButtons != ReadMemoryChoose(numberButton1, processHandle, moduleHandle):
                nButtons = nButtons + 1
                if nButtons == 32: 
                    nButtons = 0
                #check buttons pressed against frames since
                #fSince = fSince + ReadMemoryChoose(frameSince1, processHandle, mod)
 #############################           
                if ReadMemoryChoose(frameSince1, processHandle, moduleHandle) == ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, (nButtons)*8):
                    classification = ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, (nButtons)*8+4)
                else:                
                    classification = ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, (nButtons)*8)
                if directionTest(classification)==True:
                    directionMV = classification
                newButtonPressed = 1
                #    print "does this happeen"
                #nButtons = nButtons + 1
                #if nButtons == 32: 
                #    nButtons = 0
            else:
                classification = directionMV
                newButtonPressed = 0
            if saveString != "" :
                saveString = saveString + str(classification) + " , "+ str(newButtonPressed)+"\n"
  ###############################
        
            buttonsPressed = ""
            framesSince = ""
            #classification = 0
            
            if len(fSince) > 31:
                fSince.pop(0)
            i_=0
            for n in range(0,32):
                n_ = nButtons -n
                if n_ < 0:
                    n_ = 32+ n_ 

                if directionTest(ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8+4)) != True and moveTest(ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8) )== True:
                    buttonsPressed = buttonsPressed + str(ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8)) + " , " 
                    fSince.append(ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8+4))
                elif directionTest(ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8+4)) != True:
                    buttonsPressed = buttonsPressed + str(ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8)) + " , " 
                    fSince.append(ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8+4))                    
                else:
                    buttonsPressed = buttonsPressed + str(ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8+4))+ " , " 
                    fSince.append(ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8))
                if i_ > 8 :
                    break
                i_=i_+1
                
                
               # print ReadMemoryChoose(frameSince1, processHandle, moduleHandle)
            for sF in range(0,len(fSince)):
                if sF == 0:
                    framesSince = framesSince + str(ReadMemoryChoose(frameSince1, processHandle, moduleHandle)) + " , " 
                else:
                    sFsum = 0
                    for nextFrame in fSince[:sF]: sFsum = sFsum + nextFrame
                    framesSince = framesSince  + str(sFsum+ReadMemoryChoose(frameSince1, processHandle, moduleHandle))+ " , " 
            
            fSince=[]
            if (mvState1 == ReadMemoryChoose(moveState1, processHandle, moduleHandle)):
                framesInMvState1 = framesInMvState1 + 1
            else:
                framesInMvState1 = 0
            if(mvState2 == ReadMemoryChoose(moveState2, processHandle, moduleHandle)):
                framesInMvState2 = framesInMvState2 + 1
            else:
                framesInMvState2 = 0

            saveStringP1_ =  str(ReadMemoryChoose(character1, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(health1, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(ultra1, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(special1, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(positionX1, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(positionY1, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(moveState1, processHandle, moduleHandle))+" , "+\
                                str(framesInMvState1)+" , "+\
                                buttonsPressed+\
                                framesSince
            saveStringP2_ =  str(ReadMemoryChoose(character2, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(health2, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(ultra2, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(special2, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(positionX2, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(positionY2, processHandle, moduleHandle))+" , "+\
                                str(ReadMemoryChoose(moveState2, processHandle, moduleHandle))+" , "+\
                                str(framesInMvState2)+ " , "
            mvState1 = ReadMemoryChoose(moveState1, processHandle, moduleHandle)
            mvState2 = ReadMemoryChoose(moveState2, processHandle, moduleHandle)

           # print framesInMvState, " frames in state"
           # print buttonsPressed
           # print ""
           # print framesSince
            i = i+1
            if ReadMemoryChoose(health1, processHandle, moduleHandle) > 0.0 and ReadMemoryChoose(health2, processHandle, moduleHandle) > 0.0:
                f.write(saveString) # + saveStringP2)
                #print saveString
            if (ReadMemoryChoose(positionX1, processHandle, moduleHandle) > 0 ) and  (ReadMemoryChoose(positionX1, processHandle, moduleHandle) > ReadMemoryChoose(positionX1, processHandle, moduleHandle)):
                saveStringP2_ = saveStringP2_ + str(ReadMemoryChoose(positionX1, processHandle, moduleHandle) - ReadMemoryChoose(positionX2, processHandle, moduleHandle)) + " , "
            else:
                saveStringP2_ = saveStringP2_ + str(ReadMemoryChoose(positionX2, processHandle, moduleHandle) - ReadMemoryChoose(positionX1, processHandle, moduleHandle)) + " , "
            saveString = saveStringP1_ + saveStringP2_ 
        #
    #

    f.close()
    return 0
##########################
#Open program and obtain handle for Street Fighter window and vectorize
def main():
    
    windowName, exeName = ReadGameName()
    PROCESS_ALL_ACCESS = 0x1F0FFF  #identifies the rights i have to rea/edit
    pid = 0

    hwn = FindWindow(None, windowName)
    if(hwn == 0):
        print "Window not found."
        return
    else:
        pid = win32process.GetWindowThreadProcessId(hwn)
        if (pid == 0):
            print "PID was zero"
            return
########
#Find SSFIV.exe module handle to find base address
            
    #Opens STreet Fighter process, associated with SSFIVAE window
    processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid[1])

   # mi = MODULEINFO()
    mod = None
    for modules in win32process.EnumProcessModules(processHandle) :
        delimMods = win32process.GetModuleFileNameEx(processHandle, modules).split("\\")
        #print delimMods[-1], " ", exeName
        if( delimMods[-1] == exeName):
          #  print modules
          #  print GetModuleInformation(processHandle, modules, byref(mi), sizeof(mi))   #Did we get our infor
            mod = modules
            break

    i = 0
    T = True
    F = False
    continue_ = True
    
    print hwn
    win32gui.SetForegroundWindow(hwn)
    while continue_ == True:
        createTrainingFile(processHandle, mod, "DeeJay", "ThothvAiRyu", i)
        i = i+1
        continue_ = input("Continue: ")
        if continue_ == T:
            win32gui.SetForegroundWindow(hwn)
    print i, " File(s) have been created"
#    globalFrames, globalPause, globalHMS = ReadGlobal()
#    while ReadMemoryChoose(globalHMS, processHandle, mod) == 1:
#        print ReadMemoryChoose(globalHMS, processHandle, mod)
    CloseHandle(processHandle)
    
if __name__ == "__main__":
    main()