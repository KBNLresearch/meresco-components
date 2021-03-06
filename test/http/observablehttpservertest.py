## begin license ##
#
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core".
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2010-2011 Stichting Kennisnet http://www.kennisnet.nl
# Copyright (C) 2012, 2015 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012 Stichting Bibliotheek.nl (BNL) http://stichting.bibliotheek.nl
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

from seecr.test import SeecrTestCase, CallTrace
from seecr.test.portnumbergenerator import PortNumberGenerator

from weightless.core import compose

from meresco.components.http import ObservableHttpServer
from meresco.components.http.utils import CRLF


class ObservableHttpServerTest(SeecrTestCase):
    def testSimpleHandleRequest(self):
        observer = CallTrace('Observer', methods={'handleRequest': lambda *a, **kw: (x for x in [])})
        s = ObservableHttpServer(CallTrace('Reactor'), 1024)
        s.addObserver(observer)

        list(compose(s.handleRequest(RequestURI='http://localhost')))
        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        self.assertEquals('handleRequest', method.name)
        self.assertEquals(0, len(method.args))
        self.assertEquals(7, len(method.kwargs))

    def testHandleRequest(self):
        observer = CallTrace('Observer', methods={'handleRequest': lambda *a, **kw: (x for x in [])})
        s = ObservableHttpServer(CallTrace('Reactor'), 1024)
        s.addObserver(observer)

        list(compose(s.handleRequest(RequestURI='http://localhost/path?key=value&emptykey#fragment')))
        self.assertEquals(1, len(observer.calledMethods))
        method = observer.calledMethods[0]
        self.assertEquals('handleRequest', method.name)
        self.assertEquals(0, len(method.args))
        self.assertEquals(7, len(method.kwargs))
        self.assertTrue('arguments' in method.kwargs, method.kwargs)
        arguments = method.kwargs['arguments']
        self.assertEquals(2, len(arguments))
        self.assertEquals(['emptykey', 'key'], sorted(arguments.keys()))
        self.assertEquals(['value'], arguments['key'])
        self.assertEquals([''], arguments['emptykey'])

    def testMaxConnectionsErrorHandling(self):
        observer = CallTrace('Observer', methods={'handleRequest': lambda *a, **kw: (x for x in [])})
        reactor = CallTrace('Reactor')

        s = ObservableHttpServer(reactor, 1024, maxConnections=5)
        s.addObserver(observer)
        result = ''.join(s._error(ResponseCode=503, something='bicycle'))

        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals('logHttpError', observer.calledMethods[0].name)
        self.assertEquals({'ResponseCode': 503, 'something': 'bicycle'}, observer.calledMethods[0].kwargs)
        header, body = result.split(CRLF * 2)
        self.assertTrue(header.startswith('HTTP/1.0 503'), header)
        self.assertTrue('Service Unavailable' in body, body)

    def testErrorHandlerRegisteredOnWeightlessHttpServer(self):
        reactor = CallTrace('Reactor')

        s = ObservableHttpServer(reactor, 1024, maxConnections=5)
        s.startServer()

        acceptor = s._httpserver._acceptor
        httphandler = acceptor._sinkFactory('sok')
        errorHandler = httphandler._errorHandler
        self.assertTrue(errorHandler == s._error)

    def testSetMaximumConnections(self):
        reactor = CallTrace('Reactor')

        s = ObservableHttpServer(reactor, 2048, maxConnections=5)
        s.startServer()

        httpserver = s._httpserver
        self.assertEquals(5, httpserver._maxConnections)
        s.setMaxConnections(6)
        acceptor = s._httpserver
        self.assertEquals(6, httpserver._maxConnections)
        self.assertEquals(6, httpserver._acceptor._sinkFactory('a sink')._maxConnections)

    def testCompressResponseFlag(self):
        reactor = CallTrace('Reactor')

        s = ObservableHttpServer(reactor, 0)
        s.startServer()
        httpserver = s._httpserver
        self.assertEquals(True, httpserver._compressResponse)

        s = ObservableHttpServer(reactor, 0, compressResponse=True)
        s.startServer()
        httpserver = s._httpserver
        self.assertEquals(True, httpserver._compressResponse)

        s = ObservableHttpServer(reactor, 0, compressResponse=False)
        s.startServer()
        httpserver = s._httpserver
        self.assertEquals(False, httpserver._compressResponse)

    def testServerWithPrio(self):
        reactor = CallTrace('reactor')
        s = ObservableHttpServer(reactor, 2000, prio=3)
        s.observer_init()
        self.assertEquals(['addReader'], reactor.calledMethodNames())
        self.assertEquals(3, reactor.calledMethods[0].kwargs['prio'])

    def testServerBindAddress(self):
        reactor = CallTrace()
        port = PortNumberGenerator.next()
        server = ObservableHttpServer(reactor, port, bindAddress='127.0.0.1')
        server.startServer()
        self.assertEquals(('127.0.0.1', port), server._httpserver._acceptor._sok.getsockname())
