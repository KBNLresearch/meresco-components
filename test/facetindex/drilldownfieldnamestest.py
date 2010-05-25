## begin license ##
#
#    Meresco Components are components to build searchengines, repositories
#    and archives, based on Meresco Core.
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2009 Delft University of Technology http://www.tudelft.nl
#    Copyright (C) 2009 Tilburg University http://www.uvt.nl
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2010 Stichting Kennisnet http://www.kennisnet.nl
#
#    This file is part of Meresco Components.
#
#    Meresco Components is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Meresco Components is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Meresco Components; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
from cq2utils import CQ2TestCase, CallTrace
from meresco.components.facetindex import DrilldownFieldnames
from meresco.components.facetindex.drilldown import NoFacetIndexException

class DrilldownFieldnamesTest(CQ2TestCase):

    def testDrilldownFieldnames(self):
        d = DrilldownFieldnames(lookup=lambda name: 'drilldown.'+name)
        observer = CallTrace('drilldown')
        observer.returnValues['drilldown'] = [('drilldown.field1', [('term1',1)]),('drilldown.field2', [('term2', 2)])]
        d.addObserver(observer)

        result = list(d.drilldown('docset', [('field1', 0, True),('field2', 3, False)]))

        self.assertEquals(1, len(observer.calledMethods))
        self.assertEquals([('drilldown.field1', 0, True),('drilldown.field2', 3, False)], list(observer.calledMethods[0].args[1]))

        self.assertEquals([('field1', [('term1',1)]),('field2', [('term2', 2)])], result)


    def testReverseLookupInException(self):
        d = DrilldownFieldnames(lookup=lambda name: 'drilldown.'+name)
        observer = CallTrace('drilldown')
        observer.exceptions['drilldown'] = NoFacetIndexException('drilldown.wrongfield', ['field0', 'field1'])
        d.addObserver(observer)

        try:
            d.drilldown('docset', [('wrongfield',0,True)])
            self.fail()
        except NoFacetIndexException, e:
            self.assertEquals("No facetindex for field 'wrongfield'. Available fields: 'field0', 'field1'", str(e))
            self.assertEquals('wrongfield', e.field)

