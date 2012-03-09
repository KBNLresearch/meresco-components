# -*- coding: utf-8 -*-
## begin license ##
# 
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core". 
# 
# Copyright (C) 2006-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2006-2012 Stichting Kennisnet http://www.kennisnet.nl
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

from meresco.core import Observable, Transparant

from time import time
from urllib import urlencode

class QueryLog(Observable):
    """
    Log incoming http queries with ip-address, path, size, timestamp, duration
    """

    def __init__(self, log, loggedPaths, backwardsCompatibility=True):
        Observable.__init__(self)
        self._log = log
        self._loggedPaths = loggedPaths
        self._backwardsCompatibility = backwardsCompatibility
        if self._backwardsCompatibility:
            from warnings import warn
            warn("Running in BackwardsCompatibility mode, adding 'queryArguments' as variable to the callstack.", DeprecationWarning)

    def handleRequest(self, Client, path, **kwargs):
        if not any(path.startswith(p) for p in self._loggedPaths):
            return self.all.handleRequest(Client=Client, path=path, **kwargs)
        return self._handleRequest(Client=Client, path=path, **kwargs)
        
    def _handleRequest(self, Client, path, **kwargs):
        _queryArguments = {}
        if self._backwardsCompatibility:
            __callstack_var_queryArguments__ = _queryArguments
        __callstack_var_queryLogValues__ = {'queryArguments':_queryArguments}

        timestamp = self._time()
        ipAddress = Client[0]
        sizeInBytes = 0
        for response in self.all.handleRequest(Client=Client, path=path, **kwargs):
            if hasattr(response, '__len__'):
                sizeInBytes += len(response)
            yield response
        size = sizeInBytes / 1024.0
        duration = self._time() - timestamp
        queryArguments = str(urlencode(sorted(_queryArguments.items()), doseq=True))
        numberOfRecords = __callstack_var_queryLogValues__.get('numberOfRecords', None)

        self._log.log(timestamp=timestamp,
                path=path,
                ipAddress=ipAddress,
                size=size,
                duration=duration,
                queryArguments=queryArguments,
                numberOfRecords=numberOfRecords)

    def _time(self):
        return time()

    def unknown(self, method, *args, **kwargs):
        return self.all.unknown(method, *args, **kwargs)


SKIP_ARGS = ['sortBy', 'sortDescending']

def duplicatedInvalidArgPutInBySRUParse_GET_RID_OF_THAT_(key, kwargs):
    return '_' in key and key.replace('_','-') in kwargs

class QueryLogHelperForSru(Observable):
    def searchRetrieve(self, **kwargs):
        queryArguments = self.ctx.queryLogValues['queryArguments']
        for key, value in kwargs.items():
            if duplicatedInvalidArgPutInBySRUParse_GET_RID_OF_THAT_(key, kwargs):
                continue
            if key in SKIP_ARGS:
                continue
            queryArguments[key] = value
        return self.any.searchRetrieve(**kwargs)

class QueryLogHelper(Observable):
    def handleRequest(self, arguments, **kwargs):
        queryArguments = self.ctx.queryLogValues['queryArguments']
        queryArguments.update(arguments)
        return self.all.handleRequest(arguments=arguments, **kwargs)

class QueryLogHelperForExecuteCQL(Transparant):
    def executeCQL(self, **kwargs):
        total, recordIds = self.any.executeCQL(**kwargs)
        self.ctx.queryLogValues['numberOfRecords'] = total
        return total, recordIds
