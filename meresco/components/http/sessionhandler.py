## begin license ##
#
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core".
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2011-2017 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2014 SURF http://www.surf.nl
# Copyright (C) 2015 Koninklijke Bibliotheek (KB) http://www.kb.nl
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
from weightless.core import compose
from utils import insertHeader
from .utils import findCookies

class SessionHandler(Observable):
    def handleRequest(self, Headers, *args, **kwargs):
        sessionIds = findCookies(Headers=Headers, name=self.call.cookieName())
        cookieDict = None if len(sessionIds) <1 else self.call.validateCookie(sessionIds[0])

        if cookieDict is None:
            cookieDict = self.call.createCookie(dict())

        __callstack_var_session__ = cookieDict['value']

        yield insertHeader(
            compose(self.all.handleRequest(session=__callstack_var_session__, Headers=Headers, *args, **kwargs)),
            cookieDict['header']
        )

