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

from seecr.test import SeecrTestCase, CallTrace

from meresco.components.http import HandleRequestFilter
from meresco.core import Observable

from weightless.core import be, compose

class HandleRequestFilterTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace('Observer', methods={'handleRequest': lambda *args, **kwargs: (x for x in [])})

        self.usedKwargs = []
        def filterMethod(**kwargs):
            self.usedKwargs.append(kwargs)
            return self.result

        self.dna = be(
            (Observable(),
                (HandleRequestFilter(filterMethod),
                    (self.observer, )
                )
            )
        )

        
    def testPasses(self):
        self.result = True
        inputKwargs = dict(path='path', Method='GET')
        list(compose(self.dna.all.handleRequest(**inputKwargs)))

        self.assertEquals([('handleRequest', inputKwargs)], [(m.name, m.kwargs) for m in self.observer.calledMethods])
        self.assertEquals([inputKwargs], self.usedKwargs)

    def testYouShallNotPass(self):
        """Fly you fools!"""
        self.result = False
        inputKwargs = dict(path='path', Method='GET')
        list(compose(self.dna.all.handleRequest(**inputKwargs)))

        self.assertEquals([], [m.name for m in self.observer.calledMethods])
        self.assertEquals([inputKwargs], self.usedKwargs)
