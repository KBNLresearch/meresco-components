## begin license ##
# 
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core". 
# 
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

from weightless.http import httpget
from meresco.components.http.utils import CRLF
from lxml.etree import parse as lxmlParse
from StringIO import StringIO
from urllib import urlencode

class HttpClient(object):

    def httpGet(self, hostname, port, path, arguments, parse=True, **kwargs):
        response = yield httpget(hostname, port, '%s?%s' % (path, urlencode(arguments)))
        headers, body = response.split(CRLF*2)
        raise StopIteration((headers, lxmlParse(StringIO(body)) if parse else body))
