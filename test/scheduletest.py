## begin license ##
#
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core".
#
# Copyright (C) 2012-2013, 2016 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012-2013 Stichting Kennisnet http://www.kennisnet.nl
# Copyright (C) 2013 Maastricht University Library http://www.maastrichtuniversity.nl/web/Library/home.htm
# Copyright (C) 2013 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
# Copyright (C) 2016 Koninklijke Bibliotheek (KB) http://www.kb.nl
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
        self.assertEquals(42, s.period)

        s = Schedule(period=0)
        self.assertEquals(0, s.secondsFromNow())
        self.assertEquals(0, s.period)

    def testTimeOfDay(self):
        s = Schedule(timeOfDay='20:00')
        self.assertEquals('20:00', s.timeOfDay)
        s._utcnow = lambda: datetime.strptime("13:30", "%H:%M")
        self.assertEquals(6.5 * 60 * 60, s.secondsFromNow())

        s._utcnow = lambda: datetime.strptime("21:15", "%H:%M")
        self.assertEquals(22.75 * 60 * 60, s.secondsFromNow())

        s._utcnow = lambda: datetime.strptime("20:00", "%H:%M")
        self.assertEquals(24 * 60 * 60, s.secondsFromNow())

    def testDayOfWeekTimeOfDay(self):
        s = Schedule(dayOfWeek=5, timeOfDay='20:00')
        self.assertEquals(5, s.dayOfWeek)
        s._utcnow = lambda: datetime.strptime("15-11-2012 13:30", "%d-%m-%Y %H:%M") # This is a Thursday
        self.assertEquals(30.5 * 60 * 60, s.secondsFromNow())

        s._utcnow = lambda: datetime.strptime("14-11-2012 21:00", "%d-%m-%Y %H:%M")
        self.assertEquals(47 * 60 * 60, s.secondsFromNow())

        s._utcnow = lambda: datetime.strptime("17-11-2012 21:00", "%d-%m-%Y %H:%M")
        self.assertEquals((5 * 24 + 23) * 60 * 60, s.secondsFromNow())

        s._utcnow = lambda: datetime.strptime("16-11-2012 20:00", "%d-%m-%Y %H:%M")
        self.assertEquals(7 * 24 * 60 * 60, s.secondsFromNow())

    def testSecondsSinceEpoch(self):
        s = Schedule(secondsSinceEpoch=123) # test with ints, but works with floats as well (much harder to test due to binary representation)
        self.assertEquals(123, s.secondsSinceEpoch)
        s._time = lambda: 76
        self.assertEquals(47, s.secondsFromNow())

    def testEqualsAndHash(self):
        self.assertEquals(Schedule(timeOfDay='20:00'), Schedule(timeOfDay='20:00'))
        self.assertEquals(Schedule(period=3), Schedule(period=3))
        self.assertEquals(Schedule(timeOfDay='20:00', dayOfWeek=3), Schedule(timeOfDay='20:00', dayOfWeek=3))
        self.assertNotEqual(Schedule(timeOfDay='20:00'), Schedule(timeOfDay='20:00', dayOfWeek=3))
        self.assertEquals(Schedule(secondsSinceEpoch=42), Schedule(secondsSinceEpoch=42))
        self.assertNotEquals(Schedule(secondsSinceEpoch=43), Schedule(secondsSinceEpoch=42))

        self.assertEquals(hash(Schedule(timeOfDay='20:00')), hash(Schedule(timeOfDay='20:00')))
        self.assertEquals(hash(Schedule(period=3)), hash(Schedule(period=3)))
        self.assertEquals(hash(Schedule(timeOfDay='20:00', dayOfWeek=3)), hash(Schedule(timeOfDay='20:00', dayOfWeek=3)))
        self.assertNotEqual(hash(Schedule(timeOfDay='20:00')), hash(Schedule(timeOfDay='20:00', dayOfWeek=3)))

        self.assertTrue(Schedule(timeOfDay='20:00') == Schedule(timeOfDay='20:00'))
        self.assertFalse(Schedule(timeOfDay='20:00') != Schedule(timeOfDay='20:00'))
        self.assertTrue(Schedule(timeOfDay='20:00') != Schedule(timeOfDay='20:00', dayOfWeek=3))
        self.assertFalse(Schedule(timeOfDay='20:00') == Schedule(timeOfDay='20:00', dayOfWeek=3))

    def testRepr(self):
        self.assertEquals('Schedule(period=0)', repr(Schedule(period=0)))
        self.assertEquals('Schedule(period=1)', repr(Schedule(period=1)))
        self.assertEquals("Schedule(timeOfDay='21:00')", repr(Schedule(timeOfDay='21:00')))
        self.assertEquals("Schedule(dayOfWeek=1, timeOfDay='21:00')", repr(Schedule(timeOfDay='21:00', dayOfWeek=1)))
        self.assertEquals("Schedule(secondsSinceEpoch=42)", repr(Schedule(secondsSinceEpoch=42)))
