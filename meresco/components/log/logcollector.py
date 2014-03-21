## begin license ##
#
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core".
#
# Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
# Copyright (C) 2014 Stichting Kennisnet http://www.kennisnet.nl
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

from meresco.core import Observable
from collections import defaultdict
from weightless.core import NoneOfTheObserversRespond, DeclineMessage, local


class LogCollector(Observable):
    """
    Log incoming http requests with ip-address, path, size, timestamp, duration
    """
    def all_unknown(self, message, *args, **kwargs):
        try:
            __callstack_var_logCollector__ = self._logCollector()
            yield self.all.unknown(message, *args, **kwargs)
        finally:
            self._writeLog(**__callstack_var_logCollector__)

    def any_unknown(self, message, *args, **kwargs):
        try:
            __callstack_var_logCollector__ = self._logCollector()
            try:
                response = yield self.any.unknown(message, *args, **kwargs)
            except NoneOfTheObserversRespond:
                raise DeclineMessage
            raise StopIteration(response)
        finally:
            self._writeLog(**__callstack_var_logCollector__)

    def do_unknown(self, message, *args, **kwargs):
        try:
            __callstack_var_logCollector__ = self._logCollector()
            self.do.unknown(message, *args, **kwargs)
        finally:
            self._writeLog(**__callstack_var_logCollector__)

    def call_unknown(self, message, *args, **kwargs):
        try:
            __callstack_var_logCollector__ = self._logCollector()
            try:
                return self.call.unknown(message, *args, **kwargs)
            except NoneOfTheObserversRespond:
                raise DeclineMessage
        finally:
            self._writeLog(**__callstack_var_logCollector__)

    @staticmethod
    def _logCollector():
        return defaultdict(list)

    def _writeLog(self, **kwargs):
        if kwargs:
            self.do.writeLog(**kwargs)


def collectLog(**kwargs):
    logCollector = local('__callstack_var_logCollector__')
    if logCollector is None:
        return
    for key, value in kwargs.items():
        logCollector[key].append(value)