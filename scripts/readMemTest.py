# -*- coding: utf-8 -*-
"""
Created on Sun Dec 14 12:56:48 2014

@author: tgunter
"""

from ctypes import *
from ctypes.wintypes import *
import struct

OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

PROCESS_ALL_ACCESS = 0x1F0FFF  #identifies the rights i have to rea/edit

pid =  3412  # I assume you have this from somewhere.
a = "\x99I@".encode("hex")
print a #struct.unpack("!f", a.decode('hex'))[0]
address =   0xA9B190 # Likewise; for illustration I'll get the .exe header.
# SSFIV.exe+69B190

buffer = c_char_p("The data goes here")
bufferSize = len(buffer.value)
bytesRead = c_ulong(0)

processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
    print "Success:", buffer, " " , bytesRead
else:
    print "Failed."

CloseHandle(processHandle)
#

##This is how I'm oging to get my pid

import psutil

name = u'SSFIV.exe'
i=0
for proc in psutil.process_iter():
    i = i +1
    print proc
    if proc._name == name:
        print proc.pid 

print i 

#"""