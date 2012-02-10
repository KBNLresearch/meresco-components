## begin license ##
# 
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core". 
# 
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
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

from weightless.core._observable import NoneOfTheObserversRespond
from meresco.core import Observable

class FilterMessages(Observable):
    def __init__(self, allowed=[], disallowed=[]):
        Observable.__init__(self)
        assert len(allowed) == 0 or len(disallowed) == 0, 'Use disallowed or allowed'
        if allowed:
            self._allowedMessage = lambda message: message in allowed
        else:
            self._allowedMessage = lambda message: message not in disallowed

    def any_unknown(self, message, *args, **kwargs):
        if self._allowedMessage(message):
            response = yield self.any.unknown(message, *args, **kwargs)
            raise StopIteration(response)
        raise self.messageNotAnswered(message)

    def messageNotAnswered(self, message):
        raise NoneOfTheObserversRespond(unansweredMessage=message, observers=[], unknownCall=True)

    def all_unknown(self, message, *args, **kwargs):
        if self._allowedMessage(message):
            yield self.all.unknown(message, *args, **kwargs)

    def call_unknown(self, message, *args, **kwargs):
        if self._allowedMessage(message):
            return self.call.unknown(message, *args, **kwargs)
        raise self.messageNotAnswered(message)

    def do_unknown(self, message, *args, **kwargs):
        if self._allowedMessage(message):
            self.do.unknown(message, *args, **kwargs)
