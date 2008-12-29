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
from itertools import islice
from sys import maxint
from ctypes import c_uint32, c_char_p, POINTER, cdll, pointer, py_object, Structure, c_ulong, c_int, cast
from docset import DocSet, libDocSet, docsetpointer

def errcheck(result, func, arguments):
    if not result:
        raise IndexError('list index out of range')
    return result

class cardinality_t(Structure):
    _fields_ = [('term',        c_char_p),
                ('cardinality', c_uint32)]

DocSetList_create = libDocSet.DocSetList_create
DocSetList_create.restype = POINTER(None)

DocSetList_delete = libDocSet.DocSetList_delete
DocSetList_delete.restype = None

DocSetList_add = libDocSet.DocSetList_add
DocSetList_add.restype = None

DocSetList_removeDoc = libDocSet.DocSetList_removeDoc
DocSetList_removeDoc.argtypes = [ POINTER(None), c_uint32 ]
DocSetList_removeDoc.restype = None

DocSetList_size = libDocSet.DocSetList_size
DocSetList_size.restype = int

DocSetList_get = libDocSet.DocSetList_get
DocSetList_get.restype = POINTER(None)
DocSetList_get.errcheck = errcheck

DocSetList_getForTerm = libDocSet.DocSetList_getForTerm
DocSetList_getForTerm.argtypes = [ POINTER(None), c_char_p ]
DocSetList_getForTerm.restype = POINTER(None)

DocSetList_combinedCardinalities = libDocSet.DocSetList_combinedCardinalities
DocSetList_combinedCardinalities.argtypes = [POINTER(None), c_int, c_int]
DocSetList_combinedCardinalities.restype = POINTER(None) #POINTER(cardinality_t)

DocSetList_fromTermEnum = libDocSet.DocSetList_fromTermEnum
DocSetList_fromTermEnum.restype = POINTER(None)

DocSetList_sortOnCardinality = libDocSet.DocSetList_sortOnCardinality
DocSetList_sortOnCardinality.restype = None
DocSetList_sortOnCardinality.argtypes = [POINTER(None)]

CardinalityList_size = libDocSet.CardinalityList_size
CardinalityList_size.argtypes = [POINTER(None)]
CardinalityList_size.restype = c_int

CardinalityList_at = libDocSet.CardinalityList_at
CardinalityList_at.argtypes = [POINTER(None), c_int]
CardinalityList_at.restype = POINTER(cardinality_t)

CardinalityList_free = libDocSet.CardinalityList_free
CardinalityList_free.argtypes = [POINTER(None)]
CardinalityList_free.restype = None

class DocSetList(object):

    @classmethod
    def fromTermEnum(clazz, termEnum, termDocs):
        r = DocSetList_fromTermEnum(py_object(termEnum), py_object(termDocs))
        return clazz(r)

    def __init__(self, cobj=None):
        if cobj:
            self._cobj = cobj
        else:
            self._cobj = DocSetList_create()
        self._as_parameter_ = self._cobj

    def __del__(self):
        DocSetList_delete(self)

    def __len__(self):
        return DocSetList_size(self)

    def __getitem__(self, i):
        item = DocSetList_get(self, i)
        return DocSet(cobj=item)

    def add(self, docset):
        if len(docset) == 0:
            return
        docset.releaseData()
        DocSetList_add(self, docset)

    def termCardinalities(self, docset, maxResults=maxint, sorted=False):
        p = DocSetList_combinedCardinalities(self, docset, maxResults, sorted)
        try:
            for i in xrange(CardinalityList_size(p)):
                c = CardinalityList_at(p, i)
                yield (c.contents.term, c.contents.cardinality)
        finally:
            CardinalityList_free(p)

    def allCardinalities(self):
        for docset in self:
            yield (docset.term(), len(docset))

    def addDocument(self, docid, terms):
        for term in terms:
            r = DocSetList_getForTerm(self, term)
            if r:
                docset = DocSet(cobj=r)
                docset.add(docid)
            else:
                docset = DocSet(term)
                docset.add(docid)
                self.add(docset)

    def deleteDoc(self, doc):
        DocSetList_removeDoc(self, doc)

    def sortOnCardinality(self):
        DocSetList_sortOnCardinality(self)
