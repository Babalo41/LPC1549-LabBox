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

class ConfigTips:
	signalsNumberTip = """The number of signals that you want to observe on the plot."""

	signalNameTip = """Name that you will see in plot's legend.
One of the signals should be named 'ADC' to observe its real time value.
Order is important!
Prefered length: 10 characters."""

	dataLengthTip = """Maximum length of indivisible information to send, in bytes.
For example, if the maximum voltage of ADC and DAC is 3300mV 
then 2 bytes will be more than enough, as 3300 < 65536."""

	maxVoltageTip = """Absolute maximum value that will be visible on y-axis."""

	zeroMirroredTip = """Show negative offset of y-axis?"""

	updateTimeTip = """Interval between reading input data packets. Also used to update plot's view.
Should be less or equal to interval that used on a microcontroller to send data!
Prefered value: from 1 to 99."""