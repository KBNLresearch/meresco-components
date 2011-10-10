# -*- coding: utf-8 -*-
## begin license ##
# 
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core". 
# 
# Copyright (C) 2010-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2010-2011 Stichting Kennisnet http://www.kennisnet.nl
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
from ipfilter import IpFilter

class Deproxy(Observable):
    def __init__(self, deproxyForIps=None, deproxyForIpRanges=None):
        Observable.__init__(self)
        if not (deproxyForIps or deproxyForIpRanges):
            raise ValueError('Expected ipaddresses to deproxy for.')
        self._ipfilter = IpFilter(allowedIps=deproxyForIps, allowedIpRanges=deproxyForIpRanges)

    def handleRequest(self, Client, Headers, **kwargs):
        clientHost, clientPort = Client
        if self._ipfilter.filterIpAddress(clientHost):
            clientHost = _firstFromCommaSeparated(Headers.get("X-Forwarded-For", clientHost))

            host = _firstFromCommaSeparated(Headers.get("X-Forwarded-Host",  Headers.get('Host', '')))
            if host != '':
                Headers['Host'] = host

        return self.all.handleRequest(Client=(clientHost, clientPort), Headers=Headers, **kwargs)

def _firstFromCommaSeparated(s):
    return s.split(",", 1)[0].strip()
