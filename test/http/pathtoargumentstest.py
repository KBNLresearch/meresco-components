## begin license ##
#
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core".
#
# Copyright (C) 2018 Seecr (Seek You Too B.V.) http://seecr.nl
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
from weightless.core import be, asString
from meresco.core import Observable

from meresco.components.http import PathToArguments, pathToArguments, argumentsToPath

class PathToArgumentsTest(SeecrTestCase):
    def testIdea(self):
        observer = CallTrace(methods=dict(handleRequest=lambda **_: (f for f in ['RESPONSE'])))
        top = be((Observable(),
            (PathToArguments(),
                (observer,)
            )
        ))
        self.assertEqual('RESPONSE', asString(top.all.handleRequest(path='/path/key1:value1/key2:value2', arguments={'key1':['value0']}, other='passed')))
        self.assertEqual(['handleRequest'], observer.calledMethodNames())
        handle = observer.calledMethods[0]
        self.assertEqual(dict(
            other='passed',
            path='/path',
            arguments={'key1': ['value0', 'value1'], 'key2': ['value2']},
            ), handle.kwargs)
