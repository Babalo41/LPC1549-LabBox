import os
import sys
import time
import serial

from collections import deque
import numpy as np
from itertools import islice

from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QMessageBox
from PyQt5 import QtGui, QtCore
from designLabbox import Ui_MainWindow
from defines import *
print("hellow world")

class LabBox(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(LabBox, self).__init__(parent)
        self.setWindowTitle('LPC1549')
        self.state = ConnectionState.DISCONNECTED
        self.port = None
        self.timer = QtCore.QTimer()
        self.lineColors = ['b', 'g', 'r']
        self.cfgData = CfgData()
        self.pointsNumber = 1000                                                  #orignal value 1000  try1 was 5049 X rangw
        self.plotStack = {}
        
        
    def reinit(self):
        self.state = ConnectionState.DISCONNECTED
        self.port = None
        self.timer = QtCore.QTimer()
        self.cfgData = CfgData()                         #it needs to be removed!!!!!!!!!!!!!!11
        self.plotStack = {}
        self.plotStack["time"] = np.arange(0, self.pointsNumber, 3)                             # orignal value 0 to 1 Y rane

        ###GUI setups###
    def customSetupUI(self):
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.statusBar().setSizeGripEnabled(False)
        self.dacLineEdit.setEnabled(True)                                                                     #disable dac value box  for safety
        self.ConnectButton.clicked.connect(self.connectBtnOnclick)
        self.SetButton.clicked.connect(self.setButtonOnclick)
        self.sineRadioButton.toggled.connect(lambda: self.changeSignalFunction(SignalMode.SINE))
        self.rampRadioButton.toggled.connect(lambda: self.changeSignalFunction(SignalMode.RAMP))
        self.stepRadioButton.toggled.connect(lambda: self.changeSignalFunction(SignalMode.STEP))
        self.NoBiasRadioButton.toggled.connect(lambda: self.changeSignalFunction(SignalMode.NoBIAS))
        
        self.devicePathLineEdit.setText("/dev/ttyACM0")
        self.deviceBaudrateLineEdit.setText("115200")
        self.plotView.setBackground(QtGui.QColor(0xef, 0xef, 0xef))
        self.plotView.plot.setContentsMargins(10, 0, 10, 0)
        self.plotView.plot.setXRange(0, self.pointsNumber, padding=0)
        #self.plotView.plot.enableAutoRange('x', True)
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("./img/gear.png"))

        self.enablePanel(False)



    def openCfgDialog(self):
        self.cfgDialog = Config()
        self.cfgDialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.cfgDialog.setFixedSize(self.cfgDialog.size())
        self.cfgDialog.show()
        self.cfgDialog.exec_()

    def closeEvent(self, event):
        if self.state == ConnectionState.CONNECTED:
            self.disconnectMicro()
        event.accept()


    def enablePanel(self, state):
        self.signalFunctionBox.setEnabled(state)
        
    def setButtonOnclick(self):
        self.dacLineEdit.setEnabled(True)
        self.dacValue = self.dacLineEdit.text()
        print("printing the dac value ",self.dacValue)
        if self.dacValue == '':
            raise ValueError("Field 'DACmax' can't be empty!")
        try:
            isinstance(int(self.dacValue), int)
        except:
            raise ValueError("Baudrate should be an integer value!")
        
    def connectBtnOnclick(self):
        if self.state == ConnectionState.DISCONNECTED:      #connect
            try:
                self.reinit()
                self.ConnectButton.setEnabled(False)
                self.connectMicro()
                self.ConnectButton.setEnabled(True)
                self.state = ConnectionState.CONNECTED
                self.ConnectButton.setText('Disconnect')
                #self.connectionGroupBox.setEnabled(False)
                self.devicePathLineEdit.setEnabled(False)
                self.deviceBaudrateLineEdit.setEnabled(False)
                self.initPlot()
            except (ValueError, FileNotFoundError, PermissionError, RuntimeError) as e:
                QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
                self.ConnectButton.setEnabled(True)
                return
            except Exception as e:
                QMessageBox.warning(self, "Error", "Unexpected exception occured:\n"+str(e), QMessageBox.Ok)
                print("Unexpected exception occured!\n"+str(e))             
                self.connectBtnOnclick()
                raise
        elif self.state == ConnectionState.CONNECTED:       #disconnect
            try:
                self.deinitPlot()
            except Exception as e:
                QMessageBox.warning(self, "Error", "Unexpected exception occured:\n"+str(e), QMessageBox.Ok)
                print("Unexpected exception occured!")
                raise
            self.disconnectMicro()
            self.ConnectButton.setEnabled(True)
            self.ConnectButton.setText('Connect')
            self.state = ConnectionState.DISCONNECTED
            #self.connectionGroupBox.setEnabled(True)
            self.devicePathLineEdit.setEnabled(True)
            self.deviceBaudrateLineEdit.setEnabled(True)


    def connectMicro(self):
        self.openPort()
        self.configureComm()

    def openPort(self):
        self.devicePath = self.devicePathLineEdit.text()
        print(self.devicePath)
        if self.devicePath == '':
            raise ValueError("Field 'File path' can't be empty!")
        elif os.access(self.devicePath, os.F_OK) == False:
            raise FileNotFoundError("No such device found please Connect The device to PC!!!")
        elif os.access(self.devicePath, os.R_OK|os.W_OK) == False:
            raise PermissionError("Device file:\nRead and/or write permission denied! Please run the code from CMD using SUDO")
        self.deviceBaudrate = self.deviceBaudrateLineEdit.text()
        if self.deviceBaudrate == '':
            raise ValueError("Field 'Baudrate' can't be empty!")
        try:
            isinstance(int(self.deviceBaudrate), int)
        except:
            raise ValueError("Baudrate should be an integer value!")
        self.port = serial.Serial(
            port=self.devicePath,
            baudrate=int(self.deviceBaudrate),
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.2                     #100ms
            )
        self.port.flushInput()
        self.port.flushOutput()
        
        print("Port is opened...")
        pass

    def read(self, Readsize, raiseTimeout):
        try:
            data = self.port.read(Readsize)
            if data != None:
                
                return data
            elif raiseTimeout == 0.2:
                raise RuntimeError("Timeout elapsed!")
        except serial.SerialException as e:
            raise RuntimeError("Unexpected SerialException occured!\n"+str(e))
        pass
    
    def writedata(self,stringToSend):
        try:
            chrNumber=0
            self.port.reset_output_buffer()
            for chr in stringToSend:
                chrNumber= chrNumber + 1
                try:
                    self.port.write(chr.encode('ascii'))
                except serial.SerialException as e:
                    raise RuntimeError("Unexpected SerialException occured!\n"+str(e))
                except serial.SerialTimeoutException:
                    raise RuntimeError("Timeout elapsed!")
                pass
            time.sleep(0.1)
        except Exception as e:
            print("Exception occured while writing data..",e)
        pass
            
        
    def readInt(self,DataFromDevice):           #Could be changed when usb added
        if(self.sineRadioButton.isChecked()):
            currentMode = SignalMode.SINE
        elif(self.rampRadioButton.isChecked()):
            currentMode = SignalMode.RAMP
        elif(self.stepRadioButton.isChecked()):
            currentMode = SignalMode.STEP
        elif(self.NoBiasRadioButton.isChecked()):
            currentMode = SignalMode.NoBIAS
        Cmd.HostToDeviceString="{0}{1})".format(currentMode,self.dacLineEdit.text())
        print("command host to device string",Cmd.HostToDeviceString)
        self.writedata(Cmd.HostToDeviceString)
        #while self.port.in_waiting > 0:
            
        rcv = self.read(Readsize=37, raiseTimeout=False)
        #if str(Cmd.HostToDeviceString) in str(rcv.decode('ascii')):
        ValueSpliter = str(rcv.decode('ascii')).split(',')
        print(ValueSpliter)
        print("ADC value: ",ValueSpliter[3])
        print("DAC value: ",ValueSpliter[4])
        #ADCvalue=float(int(ValueSpliter[3])*0.000805860805)
        #print(ADCvalue)
        #DACvalue=float(int(ValueSpliter[4])*0.000805860805)
        #print(DACvalue)
        if DataFromDevice=='ADC':  
            return int(ValueSpliter[3])#"{:10.2f}".format(ADCvalue)                                     
        elif DataFromDevice=='DAC':
            return int(ValueSpliter[4])#"{:10.2f}".format(DACvalue)
        else:
            print("Error reading data")
                
    def configureComm(self):
        if(self.sineRadioButton.isChecked()):
            currentMode = SignalMode.SINE
        elif(self.rampRadioButton.isChecked()):
            currentMode = SignalMode.RAMP
        elif(self.stepRadioButton.isChecked()):
            currentMode = SignalMode.STEP
        elif(self.NoBiasRadioButton.isChecked()):
            currentMode = SignalMode.NoBIAS
        self.changeSignalFunction(currentMode)


    def disconnectMicro(self):
        if self.port.isOpen():
            try:
                for chr in PC_BYE:
                    self.port.write(chr.encode('ascii'))
            except Exception as e:
                pass
            self.port.flushInput()
            self.port.flushOutput()
            self.port.close()
            print("closing the port.....")
            pass

    def initPlot(self):
        self.plotView.plot.addLegend()
        self.plotView.plot.setYRange(0, self.cfgData.maxVoltage, padding=0, update=False)
        #self.plotView.plot.enableAutoRange('xy', True)
        for name in self.cfgData.namesDict:
            self.plotView.traces[name] = self.plotView.plot.plot(
                pen=self.lineColors[self.cfgData.namesDict.index(name)], name=name)                              #it sets the colour and name of the line
            self.plotStack[name] = deque(maxlen=self.pointsNumber)                             #deque([], maxlen=self.pointsNumber))
        self.enablePanel(True)                                                                # it enables the panel which changes the mode of signal
        
        self.timer.timeout.connect(self.updatePlot)
        self.timer.start(self.cfgData.updateTime)

    def updatePlot(self):
        try:
            for name in self.cfgData.namesDict:
                print(name)
                data = self.readInt(DataFromDevice=name)
                print("i m updateplot")
                self.plotStack[name].append(data)
                if name == 'ADC':                                                                                    #hereADC value can be printed on GUI
                    self.ADClineEdit.setText(str(data))
                print(self.plotStack["time"][:len(self.plotStack[name])])
                print(self.plotStack[name])
                self.plotView.traces[name].setData(
                    self.plotStack["time"][:len(self.plotStack[name])],
                    self.plotStack[name])
                   
        except RuntimeError as e:
            self.connectBtnOnclick()
            QMessageBox.warning(self, "Error in UpdatePlot", str(e), QMessageBox.Ok)

    def deinitPlot(self):
        self.timer.stop()
        for name in self.cfgData.namesDict:
            self.plotStack[name].clear()
            self.plotView.traces[name].setData(
                self.plotStack["time"][:len(self.plotStack[name])],
                self.plotStack[name])
        self.ADClineEdit.setText("00")
        self.plotView.plot.legend.scene().removeItem(self.plotView.plot.legend)
        self.enablePanel(False)

    def hideBaudrateField(self, state):
        if state == False:
            self.deviceBaudrateLabel.show()
            self.deviceBaudrateLineEdit.show()
        else:
            self.deviceBaudrateLabel.hide()
            self.deviceBaudrateLineEdit.hide()

    def changeSignalFunction(self, SignalMode):
        print("printing from change signal",self.dacLineEdit.text())
        Cmd.HostToDeviceString="{0}{1})".format(SignalMode,self.dacLineEdit.text())
        print(" data string in a proper format..",Cmd.HostToDeviceString)
        ##self.DeviceToHostString=
        try:
            for chr in Cmd.PC_HELLO:
                self.port.write(chr.encode('ascii'))
            rcv=self.port.read(37)
            time.sleep(0.3)
            if rcv != None:
                print("Hello PC->",rcv)
            elif raiseTimeout == True:
                raise RuntimeError("Timeout elapsed!")
        except RuntimeError as e:
            QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)
        pass

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # MainWindow = QMainWindow()
    ui = LabBox()
    ui.customSetupUI()
    ui.show()
    # MainWindow.setFixedSize(MainWindow.size())
    # MainWindow.statusBar().setSizeGripEnabled(False) 
    sys.exit(app.exec_())