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
from time import time


class Schedule(object):
    def __init__(self, period=None, timeOfDay=None, dayOfWeek=None, secondsSinceEpoch=None):
        if (not period is None and not timeOfDay and not dayOfWeek and not secondsSinceEpoch) or \
            (period is None and not timeOfDay is None and not secondsSinceEpoch) or \
            (period is None and not timeOfDay and not dayOfWeek and secondsSinceEpoch):
            self.period = period
            self.timeOfDay = timeOfDay
            self.dayOfWeek = dayOfWeek
            self.secondsSinceEpoch = secondsSinceEpoch
        else:
            raise ValueError("specify either 'period' or 'timeOfDay' with optional 'dayOfWeek' or 'secondsSinceEpoch'")

    def secondsFromNow(self):
        if self.period is not None:
            return self.period
        if not self.secondsSinceEpoch is None:
            delta = self.secondsSinceEpoch - self._time()
            if delta < 0:
                delta = 60 * 60 * 24 * 365  # maximized to a year
            return delta
        targetTime = datetime.strptime(self.timeOfDay, "%H:%M")
        time = self._utcnow()
        currentTime = datetime.strptime("%s:%s:%s" % (time.hour, time.minute, time.second), "%H:%M:%S")
        timeDelta = targetTime - currentTime
        daysDelta = 0
        if self.dayOfWeek:
            daysDelta = self.dayOfWeek - time.isoweekday() + timeDelta.days
            if daysDelta < 0:
                daysDelta += 7
        seconds = daysDelta * 24 * 60 * 60 + timeDelta.seconds
        if seconds < 1:
            seconds = (7 if self.dayOfWeek else 1) * 24 * 60 * 60
        return seconds

    def _utcnow(self):
        return datetime.utcnow()

    def _time(self):
        return time()

    def __repr__(self):
        return "Schedule(%s)" % ', '.join('%s=%s' % (
            k,repr(v))
            for (k,v) in sorted(self.__dict__.items())
            if v is not None)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.period == other.period and \
            self.timeOfDay == other.timeOfDay and \
            self.dayOfWeek == other.dayOfWeek and \
            self.secondsSinceEpoch == other.secondsSinceEpoch

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
