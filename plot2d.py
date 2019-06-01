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

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import sys

class Plot2D(pg.GraphicsWindow):
	def __init__(self, parent):
		pg.GraphicsWindow.__init__(self)
		self.traces = dict()

		pg.setConfigOptions(antialias=True)
		pg.setConfigOption('foreground', 'k')

		self.plot = self.addPlot()
		self.plot.setMouseEnabled(x=False, y=False)
		self.plot.hideButtons()
		self.plot.showGrid(x=True, y=True)
