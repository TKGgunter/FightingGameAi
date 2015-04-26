# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 21:53:39 2014

@author: tgunter
"""
import win32api
import win32con
import pickle
import sklearn
from ctypes import *
from ctypes.wintypes import *
import struct
import win32gui
import win32process
import os
import vectorizeData as vD
import trainAndTest as tAT
import time
import numpy as np
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier


#win32api.keybd_event(win32con.SHIFT_PRESSED,0, win32con.KEYEVENTF_KEYUP,0)
#win32api.keybd_event(win32con.SHIFT_PRESSED,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
#win32api.keybd_event(win32con.SHIFT_PRESSED,0, win32con.KEYEVENTF_EXTENDEDKEY|win32con.KEYEVENT_KEYUP,0)
#Create data file
def botSensors(processHandle, moduleHandle, characterName, playerName, clf):


    globalFrames, globalPause, globalHME = vD.ReadGlobal()
    character1, health1, ultra1, special1, positionX1, positionY1, moveState1, numberButton1, frameSince1, buttonPressed1 = vD.ReadPlayer(1)
    character2, health2, ultra2, special2, positionX2, positionY2, moveState2, numberButton2, frameSince2, buttonPressed2 = vD.ReadPlayer(2)    
    
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
    botEyes = []
    button1 = 0
    button2 = 0

    
    print "Running..."
    while (vD.ReadMemoryChoose(globalHME, processHandle, moduleHandle) != 1) and vD.ReadMemoryChoose(globalPause, processHandle, moduleHandle) != 1 :
        
        
        frames = vD.ReadMemoryChoose(globalFrames, processHandle, moduleHandle)

        if(frames+1 ==  vD.ReadMemoryChoose(globalFrames, processHandle, moduleHandle)):
        #
            releaseButton(button1, button2)
            if nButtons != vD.ReadMemoryChoose(numberButton1, processHandle, moduleHandle):
                nButtons = nButtons + 1
                if nButtons == 32: 
                    nButtons = 0
                    
            buttonsPressed = []
            #classification = 0
            
            if len(fSince) > 31:
                fSince.pop(0)            
            for n in range(0,32):
                n_ = nButtons -n
                if n_ < 0:
                    n_ = 32+ n_ 

                if vD.directionTest(vD.ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8+4)) != True and vD.moveTest(vD.ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8) )== True:
                    buttonsPressed.append(vD.ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8)) 
                    fSince.append(vD.ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8+4))
                elif vD.directionTest(vD.ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8+4)) != True:
                    buttonsPressed.append(vD.ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8)) 
                    fSince.append(vD.ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8+4))                    
                else:
                    buttonsPressed.append(vD.ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8+4)) 
                    fSince.append(vD.ReadMemoryChoose(buttonPressed1, processHandle, moduleHandle, n_*8))
                
                
               # print ReadMemoryChoose(frameSince1, processHandle, moduleHandle)

            if (mvState1 == vD.ReadMemoryChoose(moveState1, processHandle, moduleHandle)):
                framesInMvState1 = framesInMvState1 + 1
            else:
                framesInMvState1 = 0
            if(mvState2 == vD.ReadMemoryChoose(moveState2, processHandle, moduleHandle)):
                framesInMvState2 = framesInMvState2 + 1
            else:
                framesInMvState2 = 0

            P1_ =  np.array([vD.ReadMemoryChoose(character1, processHandle, moduleHandle) ,\
                                vD.ReadMemoryChoose(health1, processHandle, moduleHandle) ,\
                                vD.ReadMemoryChoose(ultra1, processHandle, moduleHandle),\
                                vD.ReadMemoryChoose(special1, processHandle, moduleHandle),\
                                vD.ReadMemoryChoose(positionX1, processHandle, moduleHandle),\
                                vD.ReadMemoryChoose(positionY1, processHandle, moduleHandle),\
                                vD.ReadMemoryChoose(moveState1, processHandle, moduleHandle) ,\
                                framesInMvState1], dtype=float)
            P1_ = np.concatenate((P1_,buttonsPressed, fSince), 0)
            P2_ =  np.array([vD.ReadMemoryChoose(character2, processHandle, moduleHandle) ,\
                                vD.ReadMemoryChoose(health2, processHandle, moduleHandle),\
                                vD.ReadMemoryChoose(ultra2, processHandle, moduleHandle),\
                                vD.ReadMemoryChoose(special2, processHandle, moduleHandle),\
                                vD.ReadMemoryChoose(positionX2, processHandle, moduleHandle),\
                                vD.ReadMemoryChoose(positionY2, processHandle, moduleHandle),\
                                vD.ReadMemoryChoose(moveState2, processHandle, moduleHandle),\
                                framesInMvState2 ], dtype = float)
            mvState1 = vD.ReadMemoryChoose(moveState1, processHandle, moduleHandle)
            mvState2 = vD.ReadMemoryChoose(moveState2, processHandle, moduleHandle)
            
            botEyes = np.concatenate((P1_, P2_),0)
            
            print botEyes
            print clf.predict(botEyes)
            button1, button2 = pressButton(clf.predict(botEyes))
            print button1, " " , button2

           # print framesInMvState, " frames in state"
           # print buttonsPressed
           # print ""
           # print framesSince
            fSince=[]
            i = i+1

        #

    return 0
    
def pressButton(button = 0):
    #[64, 128, 256, 448, 512, 1024, 2048, 3584, 576, 1152, 2304, 192, 320, 384, 1536, 2560, 3072]
    #[0, 2, 4, 8, 10, 12,16,18,20]
    if vD.moveTest(button)==False and vD.directionTest(button)==False:
        print "unrecognized button"
        return 0, 0
    elif button == 0:
        return 0, 0
    elif button == 8:
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 8, 0
    elif button == 12:
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 8, 4
    elif button == 4:
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 4, 0
    elif button == 20:
        win32api.keybd_event(win32con.VK_RIGHT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0) 
        return 4, 16
    elif button == 16:
        win32api.keybd_event(win32con.VK_RIGHT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 16, 0
    elif button == 18:
        win32api.keybd_event(win32con.VK_RIGHT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_UP,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 16, 2
    elif button == 2:
        win32api.keybd_event(win32con.VK_UP,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 2, 0
    elif button == 10:
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_UP,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 8, 2
    #Button Presses
    elif button == 64:
        win32api.keybd_event(ord("A"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 64, 0
    elif button == 128:
        win32api.keybd_event(ord("S"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 128, 0
    elif button == 256:
        win32api.keybd_event(ord("D"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 256, 0
    elif button == 448:
        win32api.keybd_event(ord("F"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 448, 0
    elif button == 512:
        win32api.keybd_event(ord("Z"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 512, 0
    elif button == 1024:
        win32api.keybd_event(ord("X"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 1024, 0
    elif button == 2048:
        win32api.keybd_event(ord("C"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 2048, 0
    elif button == 3584:
        win32api.keybd_event(ord("V"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 3584, 0
    elif button == 576:
        win32api.keybd_event(ord("Q"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 576, 0
    elif button == 1152:
        win32api.keybd_event(ord("W"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 1152,0
    elif button == 2304:
        win32api.keybd_event(ord("E"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 2304, 0
    elif button == 64+4:
        win32api.keybd_event(ord("A"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 64, 4
    elif button == 128+4:
        win32api.keybd_event(ord("S"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 128, 4
    elif button == 256+4:
        win32api.keybd_event(ord("D"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 256, 4
    elif button == 448+4:
        win32api.keybd_event(ord("F"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 448, 4
    elif button == 512+4:
        win32api.keybd_event(ord("Z"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 512, 4
    elif button == 1024+4:
        win32api.keybd_event(ord("X"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 1024, 4
    elif button == 2048+4:
        win32api.keybd_event(ord("C"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 2048, 4
    elif button == 3584+4:
        win32api.keybd_event(ord("V"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 3584, 4
    elif button == 576+4:
        win32api.keybd_event(ord("Q"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 576, 4
    elif button == 1152+4:
        win32api.keybd_event(ord("W"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 1152,4
    elif button == 2304+4:
        win32api.keybd_event(ord("E"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 2304, 4
    elif button == 64+8:
        win32api.keybd_event(ord("A"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 64, 8
    elif button == 128+8:
        win32api.keybd_event(ord("S"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 128, 8
    elif button == 256+8:
        win32api.keybd_event(ord("D"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 256, 8
    elif button == 448+8:
        win32api.keybd_event(ord("F"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 448, 8
    elif button == 512+8:
        win32api.keybd_event(ord("Z"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 512, 8
    elif button == 1024+8:
        win32api.keybd_event(ord("X"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 1024, 8
    elif button == 2048+8:
        win32api.keybd_event(ord("C"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 2048, 8
    elif button == 3584+8:
        win32api.keybd_event(ord("V"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 3584, 8
    elif button == 576+8:
        win32api.keybd_event(ord("Q"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 576, 8
    elif button == 1152+8:
        win32api.keybd_event(ord("W"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 1152,8
    elif button == 2304+8:
        win32api.keybd_event(ord("E"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
        return 2304, 8
    else :
        print button, "HAS NOT BEEN IMPLEMENTED"
        return 0, 0
    
    #[64, 128, 256, 448, 512, 1024, 2048, 3584, 576, 1152, 2304, 192, 320, 384, 1536, 2560, 3072]
    #win32api.keybd_event(win32con.SHIFT_PRESSED,0, win32con.KEYEVENTF_EXTENDEDKEY,0)

    #Double Button test
    win32api.keybd_event(ord("S"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
    win32api.keybd_event(ord("X"),0, win32con.KEYEVENTF_EXTENDEDKEY,0)
    time.sleep(.3)
    win32api.keybd_event(ord("S"),0, win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(ord("X"),0, win32con.KEYEVENTF_KEYUP,0)
    print "a"
    
    
    #Movement test
    win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
    time.sleep(1)
    win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_KEYUP,0)
    #win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_EXTENDEDKEY|win32con.KEYEVENTF_KEYUP,0)
    
def releaseButton(button1 = 0, button2=0):
    #win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_KEYUP,0)
    buttons = [button1, button2]
    for button in buttons:
        if button == 0:
            print "0"
        elif button == 8:
            win32api.keybd_event(win32con.VK_LEFT,0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 4:
            win32api.keybd_event(win32con.VK_DOWN,0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 16:
            win32api.keybd_event(win32con.VK_RIGHT,0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 2:
            win32api.keybd_event(win32con.VK_UP,0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 64:
            win32api.keybd_event(ord("A"),0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 128:
            win32api.keybd_event(ord("S"),0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 256:
            win32api.keybd_event(ord("D"),0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 448:
            win32api.keybd_event(ord("F"),0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 512:
            win32api.keybd_event(ord("Z"),0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 1024:
            win32api.keybd_event(ord("X"),0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 2048:
            win32api.keybd_event(ord("C"),0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 3584:
            win32api.keybd_event(ord("V"),0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 576:
            win32api.keybd_event(ord("Q"),0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 1152:
            win32api.keybd_event(ord("W"),0, win32con.KEYEVENTF_KEYUP,0)
        elif button == 2304:
            win32api.keybd_event(ord("E"),0, win32con.KEYEVENTF_KEYUP,0)
        else: print ""
    
def main():
    windowName, exeName = vD.ReadGameName()
    PROCESS_ALL_ACCESS = 0x1F0FFF  #identifies the rights i have to rea/edit
    pid = 0

    hwn = vD.FindWindow(None, windowName)
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
    processHandle = vD.OpenProcess(PROCESS_ALL_ACCESS, False, pid[1])

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
        
    clf = tAT.trainCLF()
#    time_ = time.time()
#    while (time.time() - time_ ) < 60:
#        time.sleep(5)
#        pressButton()
    continue_ = True
    T = True
    F = False    

    print "Ready to fight..."
    raw_input("Press ENTER to continue")
    win32gui.SetForegroundWindow(hwn)
    while continue_ == True:
        botSensors(processHandle, mod, "Test", "ThothvAi", clf)
        continue_ = input("Continue: ")
        if continue_ == T:
            win32gui.SetForegroundWindow(processHandle)
    print " Program has ended"
    vD.CloseHandle(processHandle)

if __name__ == "__main__":
    main()
    