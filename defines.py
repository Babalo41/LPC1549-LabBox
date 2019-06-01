'''
Author: Anton Rak
Date: June 2018

This file is part of LabBox.

LabBox is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LabBox is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LabBox.  If not, see <https://www.gnu.org/licenses/>.
'''

from enum import Enum

class Cmd:
    CharString = "(?,00100000,4059)"
    HostToDeviceString= ""
    PC_HELLO = "????????????"
    PC_BYE   = "(?,00000000,0000)"

class SignalMode:
    SINE   = "(?,00100000,"
    RAMP   = "(?,01000000,"
    STEP   = "(?,10000000,"
    NoBIAS = "(?,00000001,"

class ConnectionState:
    CONNECTED, DISCONNECTED = range(2)

class CfgData:
    def __init__(self):     
        self.namesDict = ["ADC" , "DAC"]
        self.maxVoltage = 8000
        self.zeroMirrored = False
        self.updateTime = 0