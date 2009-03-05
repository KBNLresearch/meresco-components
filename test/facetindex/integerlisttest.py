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
from cq2utils import CQ2TestCase
from time import time

from merescocomponents.facetindex import IntegerList

class IntegerListTest(CQ2TestCase):

    def testConstruct(self):
        l = IntegerList()
        self.assertEquals(0, len(l))
        l = IntegerList(10)
        self.assertEquals(10, len(l))
        self.assertEquals([0,1,2,3,4,5,6,7,8,9], list(l))

    def testAppend(self):
        l = IntegerList()
        l.append(4)
        self.assertEquals([4], list(l))
        l.append(8)
        self.assertEquals([4,8], list(l))

    def testLen(self):
        l = IntegerList()
        self.assertEquals(0, len(l))

        l.append(1)
        self.assertEquals(1, len(l))

    def testIndex(self):
        l = IntegerList(100)

        self.assertEquals(0, l[0])
        self.assertEquals(66, l[66])
        self.assertEquals(99, l[-1])
        self.assertEquals(98, l[-2])
        self.assertEquals(90, l[-10])

    def testSlicing(self):
        l = IntegerList(100)
        self.assertEquals([0,1], l[:2])
        self.assertEquals([1,2,3,4], l[1:5])
        self.assertEquals([98, 99], l[98:])
        self.assertEquals([98, 99], l[-2:])

    def testCopySlice(self):
        l = IntegerList(100)
        m = l[:]
        self.assertEquals(100, len(m))

    def testExtend(self):
        l = IntegerList()
        l.extend([1,2])
        self.assertEquals(2, len(l))
        self.assertEquals([1,2], list(l))

        l.extend([3,4])
        self.assertEquals(4, len(l))
        self.assertEquals([1,2,3,4], list(l))

    def testDel(self):
        l = IntegerList()
        l.extend([1,2])
        del l[0]
        self.assertEquals(1, len(l))
        self.assertEquals([2], list(l))

    def testDelSlice(self):
        l = IntegerList(10)
        del l[5:]
        self.assertEquals([0,1,2,3,4], list(l))

    def testEquality(self):
        l1 = IntegerList(10)
        l2 = IntegerList(10)
        self.assertEquals(l1, l2)

    def testCopy(self):
        l = IntegerList(5)
        copy = l.copy()
        self.assertEquals([0,1,2,3,4], list(l))
        self.assertEquals(5, len(copy))
        self.assertEquals([0,1,2,3,4], list(copy))
        l.append(9)
        copy.append(7)
        self.assertEquals([0,1,2,3,4, 9], list(l))
        self.assertEquals([0,1,2,3,4, 7], list(copy))

    def testSetItem(self):
        l = IntegerList(5)
        l[0] = 10
        self.assertEquals([10,1,2,3,4], list(l))

        l = IntegerList(5)
        l[2] = -1
        self.assertEquals([0,1,-1,3,4], list(l))

    def testDitchHolesStartingAt(self):
        l = IntegerList(5)
        l.mergeFromOffset(0)
        self.assertEquals([0,1,2,3,4], list(l))

        l = IntegerList(5)
        l[2] = -1
        l[4] = -1
        l.mergeFromOffset(0)
        self.assertEquals([0,1,3], list(l))

        l = IntegerList(5)
        l[2] = -1
        l[4] = -1
        l.mergeFromOffset(3)
        self.assertEquals([0,1,-1,3], list(l))

        l = IntegerList(5)
        for i in range(5):
            l[i] = -1
        l.mergeFromOffset(0)
        self.assertEquals([], list(l))

        l = IntegerList(5)
        l[2] = -1
        l.mergeFromOffset(2)
        self.assertEquals([0, 1, 3, 4], list(l))

    def testIndexBoundaryCheck(self):
        l = IntegerList(5)
        try:
            l[0]
            l[1]
            l[2]
            l[3]
            l[4]
            l[5]
            self.fail('must raise exception')
        except Exception, e:
            self.assertEquals('5', str(e))
        try:
            l[-1]
            l[-2]
            l[-3]
            l[-4]
            l[-5]
            l[-6]
            self.fail('must raise exception')
        except Exception, e:
            self.assertEquals('-6', str(e))

    def testSave(self):
        l1 = IntegerList(5)
        l1.save(self.tempdir+'/list.bin')
        l2 = IntegerList()
        l2.extendFrom(self.tempdir+'/list.bin')
        self.assertEquals(l1, l2)
        l2.extendFrom(self.tempdir+'/list.bin')
        self.assertEquals([0,1,2,3,4,0,1,2,3,4], l2)

    def testSaveFromOffset(self):
        l1 = IntegerList(5)
        l1.save(self.tempdir+'/list.bin', offset=3)
        l2 = IntegerList()
        l2.extendFrom(self.tempdir+'/list.bin')
        self.assertEquals([3,4], l2)

    def testSaveInvalidOffset(self):
        l1 = IntegerList(5)
        try:
            l1.save(self.tempdir+'/list.bin', offset=5)
            self.fail()
        except Exception, e:
            self.assertEquals('Invalid index: 5 [0..5)', str(e))
        try:
            l1.save(self.tempdir+'/list.bin', offset=-1)
            self.fail()
        except Exception, e:
            self.assertEquals('Invalid index: -1 [0..5)', str(e))

    def testSaveEmpty(self):
        l = IntegerList()
        l.save(self.tempdir+'/empty')
        l.extendFrom(self.tempdir+'/empty')
        self.assertEquals([], l)

    def testSaveWrongDir(self):
        l1 = IntegerList(5)
        try:
            l1.save('/doesnotexist')
            self.fail('must raise ioerror')
        except IOError, e:
            self.assertEquals("[Errno 13] No such file or directory: '/doesnotexist'", str(e))

    def testLoadWrongDir(self):
        l1 = IntegerList(5)
        try:
            l1.extendFrom('/doesnotexist')
            self.fail('must raise ioerror')
        except IOError, e:
            self.assertEquals("[Errno 2] No such file or directory: '/doesnotexist'", str(e))
        self.assertEquals([0,1,2,3,4], list(l1))

    def testLoadAndSaveSpeed(self):
        l = IntegerList(10**6)
        l1 = IntegerList()
        t0 = time()
        l.save(self.tempdir+'/list.bin')
        t1 = time()
        l1.extendFrom(self.tempdir+'/list.bin')
        t2 = time()
        tsave = t1 - t0
        tload = t2 - t1
        self.assertTrue(0.01 < tsave < 0.05, tsave)
        self.assertTrue(0.10 < tload < 0.50, tload)

    def testExtendTo(self):
        def check(expected):
            l2 = IntegerList()
            l2.extendFrom(self.tempdir+'/list.bin')
            self.assertEquals(expected, l2)

        l1 = IntegerList()
        l1.extendTo(self.tempdir + '/list.bin')
        check([])
        
        l1 = IntegerList()
        l1.append(94)
        l1.append(34)
        l1.append(81)
        
        l1.extendTo(self.tempdir + '/list.bin')
        check([94, 34, 81])

        l1 = IntegerList()
        l1.append(8)
        l1.append(4)
        l1.append(16)

        l1.extendTo(self.tempdir + '/list.bin')
        check([94, 34, 81, 8, 4, 16])
