## begin license ##
#
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core".
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2010 Delft University of Technology http://www.tudelft.nl
# Copyright (C) 2011 Stichting Kennisnet http://www.kennisnet.nl
# Copyright (C) 2012, 2014-2016 Seecr (Seek You Too B.V.) http://seecr.nl
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

from meresco.components.http import SessionHandler, utils, CookieMemoryStore
from meresco.components.http.utils import CRLF, findCookies
from weightless.core import asString, consume, asList
from weightless.http import parseHeaders
from seecr.test import CallTrace, SeecrTestCase
from seecr.zulutime import ZuluTime
from os.path import join

#Cookies RFC 2109 http://www.ietf.org/rfc/rfc2109.txt
class SessionHandlerTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.handler = SessionHandler()
        self.cookiestore = CookieMemoryStore(name='session', timeout=10)
        self.handler.addObserver(self.cookiestore)
        self.handler._zulutime = lambda: ZuluTime('2015-01-27T13:34:45Z')
        self.observer = CallTrace('Observer')
        self.handler.addObserver(self.observer)

    def testCreateSession(self):
        called = []
        def handleRequest(*args, **kwargs):
            called.append({'args':args, 'kwargs':kwargs})
            yield  utils.okHtml
            yield '<ht'
            yield 'ml/>'
        self.observer.handleRequest = handleRequest
        result = asString(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={'a':'b'}))

        self.assertEquals(1, len(called))
        session = called[0]['kwargs']['session']
        self.assertEqual({}, session)
        self.assertEquals({'a':'b'}, called[0]['kwargs']['Headers'])
        self.assertTrue(('127.0.0.1', 12345), called[0]['kwargs']['Client'])
        header, body = result.split(utils.CRLF*2,1)
        self.assertEquals('<html/>', body)
        self.assertTrue('Set-Cookie' in header, header)
        headerParts = header.split(utils.CRLF)
        self.assertEquals("HTTP/1.0 200 OK", headerParts[0])
        sessionCookie = [p for p in headerParts[1:] if 'Set-Cookie' in p][0]
        self.assertTrue(sessionCookie.startswith('Set-Cookie: session'))

    def testRetrieveCookie(self):
        sessions = []
        def handleRequest(session=None, *args, **kwargs):
            sessions.append(session)
            yield  utils.okHtml + '<html/>'
        self.observer.handleRequest = handleRequest
        headers = asString(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={})).split(CRLF*2,1)[0]
        headers = parseHeaders(headers)
        self.assertTrue('Set-Cookie' in headers, headers)
        cookie = findCookies(headers, self.cookiestore.cookieName(), 'Set-Cookie')[0]
        consume(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={'Cookie': '{0}={1}'.format(self.cookiestore.cookieName(), cookie)}))
        self.assertEquals(sessions[0], sessions[1])
        self.assertEquals(id(sessions[0]),id(sessions[1]))

    def testInjectAnyCookie(self):
        sessions = []
        def handleRequest(session=None, *args, **kwargs):
            sessions.append(session)
            yield  utils.okHtml + '<html/>'
        self.observer.handleRequest = handleRequest
        headers = asString(self.handler.handleRequest(RequestURI='/path', Client=('127.0.0.1', 12345), Headers={'Cookie': '%s=%s' % (self.cookiestore.cookieName(), 'injected_id')})).split(CRLF*2,1)[0]
        headers = parseHeaders(headers)
        self.assertTrue('injected_id' not in headers['Set-Cookie'])

    def testPassThroughOfCallables(self):
        def callableMethod():
            pass

        def handleRequest(*args, **kwargs):
            yield callableMethod
            yield "HTTP/1.0 200 OK\r\n\r\nBODY"
            yield callableMethod
            yield "THE END"

        self.observer.handleRequest = handleRequest
        result = asList(self.handler.handleRequest(Headers={}))
        self.assertEquals(callableMethod, result[0])
        self.assertEquals("HTTP/1.0 200 OK\r\n", result[1])
        self.assertEquals("\r\nBODY", result[3])
        self.assertEquals(callableMethod, result[4])
        self.assertTrue(result[2].startswith('Set-Cookie: session'), result[2])
        self.assertEquals("THE END", result[5])
