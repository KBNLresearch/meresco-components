#!/usr/local/bin/python
# -*- coding: utf-8 -*-
## begin license ##
#
#    Meresco Components are components to build searchengines, repositories
#    and archives, based on Meresco Core.
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
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
from time import time
from facetindex import DocSetList, DocSet
from lucenetestcase import LuceneTestCase
from PyLucene import Term, IndexReader
from cq2utils import Wildcard

#Facts about Lucene:
# 1.  IndexReader.open() returns a MultiIndexReader reading multiple segments
# 2.  IndexReader.termDocs(Term) just does t=termDocs(); t.seek(Term)
# 3.  IndexReader.getFieldNames() is NOT sorted, it returns a HashSet.
# 4.  IndexReader.seek(TermEnum termEnum) just does seek(termEnum.term())
# 5a. TermDocs.read(int[] docs, float[] freqs) writes directly into int[]
# 5b. while int[] being a Template subclass of java.lang.Object.
# 5c. TermDocs.seek() only sets a few vars that make read() restart with first segment
# 6.  termEnum() is complex, because of merging terms from segments
# 7a. IndexReader.docFreq(Term) scans for term and is optimized for sequential access!
# 7b. TermEnum.docFreq() is only one attribute lookup!
# CONCLUSION: The fastest way would be to let TermDocs.read(int[] docs) call add on docs,
#             which directly builds a guint32 array.  Just like FakeHitCollector does.
#             Anyway, termdocs are spit out as complete lists, not iterators.
#             So, DocSet either accepts a List, or a ctypes c_uint32 array, of which
#             it assumes ownership. Both are supported by DocSet.__init__.

class DocSetListTest(LuceneTestCase):

    def testCreate(self):
        docsetlist = DocSetList()
        self.assertEquals(0, len(docsetlist))

    def testCreate2(self):
        docsetlist = DocSetList()
        self.assertEquals(0, len(docsetlist))
        try:
            docsetlist[0]
            self.fail('must raise IndexError')
        except IndexError, e:
            self.assertEquals('list index out of range', str(e))

    def testAddMore(self):
        docsetlist = DocSetList()
        docsetlist.add(DocSet('', [1,2]))
        docsetlist.add(DocSet('', [3,4]))
        docsetlist.add(DocSet('', [5,6]))
        self.assertEquals(3, len(docsetlist))
        self.assertEquals(DocSet('', [1,2]), docsetlist[0])
        self.assertEquals(DocSet('', [3,4]), docsetlist[1])
        self.assertEquals(DocSet('', [5,6]), docsetlist[2])
        try:
            docsetlist[3]
            self.fail('must raise IndexError')
        except IndexError, e:
            self.assertEquals('list index out of range', str(e))

    def testAddMoreThanBufferSize(self):
        docsetlist = DocSetList()
        bufferSize = 1000
        for i in xrange(bufferSize):
            docsetlist.add(DocSet('', [1]))
        try:
            docsetlist.add(DocSet('', [99,87]))
        except IndexError, e:
            self.fail('must not raise exception')
        self.assertEquals(bufferSize+1, len(docsetlist))
        self.assertEquals(DocSet('', [99,87]), docsetlist[bufferSize])

    def testDoNotFreeMemory1(self):
        docsetlist = DocSetList()
        d1 = DocSet('', [8])
        docsetlist.add(d1)
        del d1
        self.assertEquals(8, docsetlist[0][0])

    def testDoNotFreeMemory2(self):
        docsetlist = DocSetList()
        d1 = DocSet('', [8])
        docsetlist.add(d1)
        d1_copy = docsetlist[0]
        del d1_copy
        self.assertEquals(8, docsetlist[0][0])

    def testCheckForDuplicateAdd(self):
        docsetlist = DocSetList()
        d1 = DocSet('', [8])
        docsetlist.add(d1)
        try:
            docsetlist.add(d1)
        except AssertionError, e:
            self.assertEquals('object already released, perhaps duplicate add()?', str(e))

    def testCombinedCardinalityMultiple(self):
        docsetlist = DocSetList()
        d1 = DocSet('term1', [1,2,3])
        d2 = DocSet('term2', [2,3,4])
        d3 = DocSet('term3', [3,4,5])
        docsetlist.add(d1)
        docsetlist.add(d2)
        docsetlist.add(d3)
        x = DocSet('', [2,3,4])
        cards = docsetlist.termCardinalities(x)
        c = cards.next()
        self.assertEquals(('term1',2), c)
        self.assertEquals(('term2',3), cards.next())
        self.assertEquals(('term3',2), cards.next())
        try:
           cards.next()
           self.fail('must raise StopIteration')
        except StopIteration:
           pass

    def testCombinedCardinalityMultipleWithZeros(self):
        docsetlist = DocSetList()
        d1 = DocSet('t0', [1,2,3])
        d2 = DocSet('t1', [7,8,9]) # intersection empty
        d3 = DocSet('t2', [3,4,5])
        docsetlist.add(d1)
        docsetlist.add(d2)
        docsetlist.add(d3)
        cards = docsetlist.termCardinalities(DocSet('', [3,4]))
        self.assertEquals(('t0',1), cards.next())
        self.assertEquals(('t2',2), cards.next())
        cards = docsetlist.termCardinalities(DocSet('', [3,4]))
        self.assertEquals([('t0',1), ('t2',2)], list(cards))

    def testReadTermsFrom_SEGMENT_reader(self):
        self.createBigIndex(10, 1) # 10 records, two values 0 and 1
        termDocs = self.reader.termDocs()
        fields = self.reader.getFieldNames(IndexReader.FieldOption.ALL)
        termEnum = self.reader.terms(Term(fields[0],''))
        dsl = DocSetList.fromTermEnum(termEnum, termDocs)
        #for docset in dsl: print docset
        self.assertEquals(2, len(dsl)) # two different values/terms
        self.assertEquals(10, len(dsl[0]) + len(dsl[1]))

    def testReadTermsFrom_MULTI_reader(self):
        self.createBigIndex(13, 2) # 13 records, three values 0, 1 and 2
        termDocs = self.reader.termDocs()
        fields = self.reader.getFieldNames(IndexReader.FieldOption.ALL)
        termEnum = self.reader.terms(Term(fields[0],''))
        dsl = DocSetList.fromTermEnum(termEnum, termDocs)
        #for docset in dsl: print docset
        self.assertEquals(3, len(dsl)) # three different values/terms
        self.assertEquals(13, len(dsl[0]) + len(dsl[1]) + len(dsl[2]))

    def testGetTerms(self):
        self.createBigIndex(9, 2) # 10 records, 6 values
        termEnum = self.reader.terms(Term('field0',''))
        termDocs = self.reader.termDocs()
        dsl = DocSetList.fromTermEnum(termEnum, termDocs)
        cs = dsl.termCardinalities(DocSet('', [1,2,3,4,5,6,7,8,9]))
        NA = Wildcard()
        self.assertEquals([('t€rm0', NA), ('t€rm1', NA), ('t€rm2', NA)], list(cs))

    #def testAppendToRow(self):
    def testAppendDocument(self):
        docsetlist = DocSetList()
        docsetlist.addDocument(0, ['term0', 'term1'])
        self.assertEquals([('term0', 1), ('term1', 1)],
            list(docsetlist.termCardinalities(DocSet('', [0, 1]))))
        docsetlist.addDocument(1, ['term0', 'term1'])
        self.assertEquals([('term0', 2), ('term1', 2)],
            list(docsetlist.termCardinalities(DocSet('', [0, 1]))))
        docsetlist.addDocument(2, ['term0', 'term2'])
        self.assertEquals([('term0', 3), ('term1', 2), ('term2', 1)],
            list(docsetlist.termCardinalities(DocSet('', [0, 1, 2]))))
        try:
            docsetlist.addDocument(2, ['term0', 'term2'])
            self.fail('must raise exception')
        except Exception, e:
            self.assertTrue("non-increasing" in str(e))

    def testEmpty(self):
        m = DocSetList()
        c = list(m.termCardinalities(DocSet('y', [])))
        self.assertEquals([], list(c))
        c = list(m.allCardinalities())
        self.assertEquals([], list(c))

    def testEmptyDoc(self):
        m = DocSetList()
        n = m.add(DocSet('a', []))
        c = m.termCardinalities(DocSet('',[1]))
        self.assertEquals([], list(c))

    def testNoResultLeft(self):
        m = DocSetList()
        n = m.add(DocSet('b', [1]))
        c = m.termCardinalities(DocSet('', [2]))
        self.assertEquals([], list(c))

    def testNoResultRight(self):
        m = DocSetList()
        n = m.add(DocSet('x', [2]))
        c = m.termCardinalities(DocSet('y', [1]))
        self.assertEquals([], list(c))

    def testAdd(self):
        m = DocSetList()
        m.add(DocSet('x', [0, 2, 4, 6, 8]))
        self.assertEquals([0, 2, 4, 6, 8], m[0])
        m.add(DocSet('x', [1, 3, 5, 7, 9]))
        self.assertEquals([1, 3, 5, 7, 9], m[1])

    def testBugCausesAbort(self):
        m = DocSetList()
        m.add(DocSet('x', [100000000]))
        m[0].add(100000001)

    def testDocSetCardinalities(self):
        m = DocSetList()
        m.add(DocSet('x', [1, 3, 5, 7, 9]))
        m.add(DocSet('y', [0, 2]))
        self.assertEquals([('x', 5), ('y', 2)], list( m.allCardinalities()))

    def testtermCardinalitiesOfOne(self):
        m = DocSetList()
        m.add(DocSet('x', [0]))
        m.add(DocSet('y', [1]))
        self.assertEquals([('x', 1), ('y', 1)], list(m.termCardinalities(DocSet('z', [0, 1]))))
        self.assertEquals([('x', 1)], list(m.termCardinalities(DocSet('z', [0]))))
        self.assertEquals([('y', 1)], list(m.termCardinalities(DocSet('z', [1]))))

    def testtermCardinalitiesOfTwo(self):
        m = DocSetList()
        n = m.add(DocSet('x', [0, 2]))
        n= m.add(DocSet('y', [1, 3]))
        self.assertEquals([('x', 2)], list(m.termCardinalities(DocSet('y', [0, 2]))))
        self.assertEquals([('y', 2)], list(m.termCardinalities(DocSet('y', [1, 3]))))
        self.assertEquals([('x', 2), ('y', 2)], list(m.termCardinalities(DocSet('y', [0, 1, 2, 3]))))
        self.assertEquals([('x', 1)], list(m.termCardinalities(DocSet('y', [0]))))
        self.assertEquals([('y', 1)], list(m.termCardinalities(DocSet('y', [1]))))
        self.assertEquals([('x', 1), ('y', 1)], list(m.termCardinalities(DocSet('y', [0, 1]))))
        self.assertEquals([('x', 1)], list(m.termCardinalities(DocSet('y', [2]))))
        self.assertEquals([('y', 1)], list(m.termCardinalities(DocSet('y', [3]))))
        self.assertEquals([('x', 1), ('y', 1)], list(m.termCardinalities(DocSet('y', [2, 3]))))

    def testAllOnes(self):
        m = DocSetList()
        m.add(DocSet('x', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))
        m.add(DocSet('y', [1, 3, 5, 8, 18]))
        self.assertEquals([('x', 1)], list(m.termCardinalities(DocSet('y', [0]))))
        self.assertEquals([('x', 3), ('y', 1)], list(m.termCardinalities(DocSet('y', [0,1,2]))))
        self.assertEquals([('x', 4), ('y', 2)], list(m.termCardinalities(DocSet('y', [0,1,2,3]))))
        self.assertEquals([('x', 5), ('y', 2)], list(m.termCardinalities(DocSet('y', [0,1,2,3,4]))))
        self.assertEquals([('x', 6), ('y', 3)], list(m.termCardinalities(DocSet('y', [0,1,2,3,4,5]))))
        self.assertEquals([('x', 7), ('y', 3)], list(m.termCardinalities(DocSet('y', [0,1,2,3,4,5,6]))))
        self.assertEquals([('x', 8), ('y', 3)], list(m.termCardinalities(DocSet('y', [0,1,2,3,4,5,6,7]))))
        self.assertEquals([('x', 9), ('y', 4)], list(m.termCardinalities(DocSet('y', [0,1,2,3,4,5,6,7,8]))))
        self.assertEquals([('x',10), ('y', 4)], list(m.termCardinalities(DocSet('y', [0,1,2,3,4,5,6,7,8,9]))))

    def testMaxResults(self):
        m = DocSetList()
        m.add(DocSet('x', [0, 1]))
        m.add(DocSet('y', [1, 2, 3]))
        m.add(DocSet('z', [1]))
        self.assertEquals(3, len(list(m.termCardinalities(DocSet('y', [1])))))
        self.assertEquals(1, len(list(m.termCardinalities(DocSet('y', [1]), maxResults=1))))
        self.assertEquals(2, len(list(m.termCardinalities(DocSet('y', [1]), maxResults=2))))

    def testColumnCleanup(self):
        m = DocSetList()
        m.add(DocSet('x', [0]))
        self.assertEquals([0], m[0])
        m[0].add(1)
        self.assertEquals([0, 1], m[0])
        m.deleteDoc(1)
        m[0].add(2)
        self.assertEquals([0,2], m[0])
        m.deleteDoc(9999)

    def testSortingOnCardinality(self):
        d = DocSetList()
        d.add(DocSet('x', [2,3]))
        d.add(DocSet('y', [1,2,3]))
        unsortedResult = d.termCardinalities(DocSet('q', [1,2,3]))
        self.assertEquals([('x', 2L), ('y', 3L)], list(unsortedResult))
        d.sortOnCardinality()
        sortedResult = d.termCardinalities(DocSet('q', [1,2,3]))
        self.assertEquals([('y', 3L), ('x', 2L)], list(sortedResult))

    def testTopList(self):
        d = DocSetList()
        d.add(DocSet('a', [1,2,3]))
        d.add(DocSet('b', [2,3,4]))
        d.add(DocSet('c', [3,4,5]))
        d.add(DocSet('d', [4,5,6]))
        unsortedResult = d.termCardinalities(DocSet('q', [3,4,5]), sorted=False)
        self.assertEquals([('a',1),('b',2),('c',3),('d',2)], list(unsortedResult))
        d.sortOnCardinality()
        sortedResult = d.termCardinalities(DocSet('q', [3,4,5]), sorted=True)
        self.assertEquals([('c',3),('b',2),('d',2),('a',1)], list(sortedResult))
        sortedResult = d.termCardinalities(DocSet('q', [3,4,5]), sorted=True, maxResults=2)
        self.assertEquals([('c',3),('b',2)], list(sortedResult))
