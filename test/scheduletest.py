## begin license ##
#
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core".
#
# Copyright (C) 2012-2013 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012-2013 Stichting Kennisnet http://www.kennisnet.nl
# Copyright (C) 2013 Maastricht University Library http://www.maastrichtuniversity.nl/web/Library/home.htm
#
# This file is part of "Meresco Components"
#
# "Meresco Components" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Components" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Components"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from datetime import datetime
from meresco.components import Schedule
from seecr.test import SeecrTestCase

class ScheduleTest(SeecrTestCase):
	def testUsePeriod(self):
		s = Schedule(period=42)
		self.assertEquals(42, s.secondsFromNow())

	def testTimeOfDay(self):
		s = Schedule(timeOfDay='20:00')
		s._time = lambda: datetime.strptime("13:30", "%H:%M")
		self.assertEquals(6.5 * 60 * 60, s.secondsFromNow())

		s._time = lambda: datetime.strptime("21:15", "%H:%M")
		self.assertEquals(22.75 * 60 * 60, s.secondsFromNow())

	def testDayOfWeekTimeOfDay(self):
		s = Schedule(dayOfWeek=5, timeOfDay='20:00')
		s._time = lambda: datetime.strptime("15-11-2012 13:30", "%d-%m-%Y %H:%M") # This is a Thursday
		self.assertEquals(30.5 * 60 * 60, s.secondsFromNow())

		s._time = lambda: datetime.strptime("14-11-2012 21:00", "%d-%m-%Y %H:%M") # This is a Wednesday
		self.assertEquals(47 * 60 * 60, s.secondsFromNow())

		s._time = lambda: datetime.strptime("17-11-2012 21:00", "%d-%m-%Y %H:%M") # This is a Wednesday
		self.assertEquals((5 * 24 + 23) * 60 * 60, s.secondsFromNow())
