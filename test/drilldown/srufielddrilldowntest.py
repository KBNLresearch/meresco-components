# -*- coding: utf-8 -*-
## begin license ##
#
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core".
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2011-2015 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012, 2014-2015 Stichting Kennisnet http://www.kennisnet.nl
# Copyright (C) 2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
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

from testhelpers import Response
from meresco.components.drilldown import SruFieldDrilldown, DRILLDOWN_HEADER

from weightless.core import compose

from cqlparser import cqlToExpression

class SruFieldDrilldownTest(SeecrTestCase):

    def testSRUParamsAndXMLOutput(self):
        firstCall = []
        def executeQuery(**kwargs):
            if not firstCall:
                firstCall.append(True)
                raise StopIteration(Response(total=5, hits=range(5)))
            else:
                raise StopIteration(Response(total=10, hits=range(10)))
            yield
        sruFieldDrilldown = SruFieldDrilldown()
        observer = CallTrace("observer")
        sruFieldDrilldown.addObserver(observer)
        observer.methods["executeQuery"] = executeQuery

        result = compose(sruFieldDrilldown.extraResponseData(sruArguments={'x-field-drilldown': ['term'], 'x-field-drilldown-fields': ['field0,field1']}, query='original'))
        self.assertEqualsWS(DRILLDOWN_HEADER + """<dd:field-drilldown>
<dd:field name="field0">5</dd:field>
<dd:field name="field1">10</dd:field></dd:field-drilldown></dd:drilldown>""", "".join(result))

        self.assertEquals(['executeQuery', 'executeQuery'], [m.name for m in observer.calledMethods])
        self.assertEquals(['query', 'query'], [','.join((m.kwargs.keys())) for m in observer.calledMethods])
        self.assertEquals(cqlToExpression('(original) AND field0=term'), observer.calledMethods[0].kwargs['query'])
        self.assertEquals(cqlToExpression('(original) AND field1=term'), observer.calledMethods[1].kwargs['query'])

    def testDrilldown(self):
        adapter = SruFieldDrilldown()
        observer = CallTrace("Observer")
        def executeQuery(**kwargs):
            raise StopIteration(Response(total=16, hits=range(16)))
            yield
        observer.methods['executeQuery'] = executeQuery
        adapter.addObserver(observer)
        def dd():
            result = yield adapter.drilldown('original', 'term', ['field0', 'field1'])
            yield result
        result = compose(dd()).next()
        self.assertEquals(2, len(observer.calledMethods))
        self.assertEquals(['executeQuery', 'executeQuery'], observer.calledMethodNames())
        self.assertEquals(cqlToExpression("(original) and field0=term"),  observer.calledMethods[0].kwargs['query'])
        self.assertEquals([("field0", 16), ("field1", 16)], result)

    def testEchoedExtraRequestData(self):
        d = SruFieldDrilldown()
        result = "".join(d.echoedExtraRequestData(sruArguments={'x-field-drilldown': ['term'], 'x-field-drilldown-fields': ['field0,field1'], 'otherArgument': ['ignored']}))
        self.assertEquals(DRILLDOWN_HEADER + '<dd:field-drilldown>term</dd:field-drilldown><dd:field-drilldown-fields>field0,field1</dd:field-drilldown-fields></dd:drilldown>', result)

