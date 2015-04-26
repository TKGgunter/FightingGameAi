# -*- coding: utf-8 -*-
"""
Created on Sat Dec 20 09:29:46 2014

@author: tgunter
"""

win32api.keybd_event(win32con.SHIFT_PRESSED,0, win32con.KEYEVENTF_UP,0)
win32api.keybd_event(win32con.SHIFT_PRESSED,0, win32con.KEYEVENTF_EXTENDEDKEY,0)
win32api.keybd_event(win32con.SHIFT_PRESSED,0, win32con.KEYEVENTF_EXTENDEDKEY|KEYEVENT_KEYUP,0)