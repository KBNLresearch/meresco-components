# -*- coding: utf-8 -*-
## begin license ##
#
#    Meresco Components are components to build searchengines, repositories
#    and archives, based on Meresco Core.
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2009-2010 Delft University of Technology http://www.tudelft.nl
#    Copyright (C) 2009 Tilburg University http://www.uvt.nl
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
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

from merescolucene import Document as LuceneDocument, Field, Fieldable, iterJ, asFloat

IDFIELD = '__id__'

class DocumentException(Exception):
    """Generic Document Exception"""
    pass

class Document(object):

    def __init__(self, anId):
        self.identifier = anId
        if not self._isValidFieldValue(anId):
            raise DocumentException("Invalid ID: '%s'" % anId)

        self._document = LuceneDocument()
        self._document.add(Field(IDFIELD, anId, Field.Store.YES, Field.Index.UN_TOKENIZED) % Fieldable)
        self._fields = [IDFIELD]
        self._tokenizedFields = []

    def _isValidFieldValue(self, anObject):
        return isinstance(anObject, basestring) and anObject.strip()

    def fields(self):
        return self._fields

    def _validFieldName(self, aKey):
        return self._isValidFieldValue(aKey) and aKey.lower() != IDFIELD

    def addIndexedField(self, aKey, aValue, tokenize = True):
        if not self._validFieldName(aKey):
            raise DocumentException('Invalid fieldname: "%s"' % aKey)

        if not self._isValidFieldValue(aValue):
            return

        self._addIndexedField(aKey, aValue, tokenize)
        self._fields.append(aKey)
        if tokenize and not aKey in self._tokenizedFields:
            self._tokenizedFields.append(aKey)

    def _addIndexedField(self, aKey, aValue, tokenize = True):
        self._document.add(Field(aKey,
                                 aValue, 
                                 Field.Store.NO,
                                 tokenize and Field.Index.TOKENIZED or Field.Index.UN_TOKENIZED
                           ) % Fieldable)

    def addToIndexWith(self, anIndexWriter):
        anIndexWriter.addDocument(self._document)

    def validate(self):
        if self._fields == [IDFIELD]:
            raise DocumentException('Empty document')

    def asDict(self):
        dictionary = {}
        for field in iterJ(self._document.getFields()):
            key = field.name()
            if not key in dictionary:
                dictionary[key] = []
            if not field.stringValue()  in dictionary[key]:
                dictionary[key].append(field.stringValue())
        return dictionary

    def tokenizedFields(self):
        return self._tokenizedFields

    def __repr__(self):
        return repr(self.asDict())