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

from __future__ import with_statement
from os.path import isdir, join, isfile
from os import makedirs, listdir, rename
from storage.storage import escapeName, unescapeName
from time import time, strftime, localtime, mktime, strptime
from itertools import ifilter, dropwhile, takewhile, chain
from merescocomponents.sorteditertools import OrIterator, AndIterator, WrapIterable
from merescocomponents import SortedFileList

from bisect import bisect_left

from merescocomponents.facetindex import LuceneDict
from berkeleydict import BerkeleyDict

MERGE_TRIGGER = 1000
class OaiJazz(object):

    def __init__(self, aDirectory):
        self._directory = aDirectory
        isdir(join(aDirectory, 'stamp2identifier')) or makedirs(join(aDirectory,'stamp2identifier'))
        isdir(join(aDirectory, 'sets')) or makedirs(join(aDirectory,'sets'))
        isdir(join(aDirectory, 'prefixes')) or makedirs(join(aDirectory,'prefixes'))
        isdir(join(aDirectory, 'prefixesInfo')) or makedirs(join(aDirectory,'prefixesInfo'))
        self._prefixes = {}
        self._sets = {}
        self._stamp2identifier = BerkeleyDict(join(self._directory, 'stamp2identifier'))
        self._tombStones = SortedFileList(join(self._directory, 'tombStones.list'), mergeTrigger=MERGE_TRIGGER)
        self._read()

    def close(self):
        #self._stamp2identifier.close()
        pass

    def addOaiRecord(self, identifier, sets=[], metadataFormats=[]):
        assert [prefix for prefix, schema, namespace in metadataFormats], 'No metadataFormat specified for record with identifier "%s"' % identifier
        oldPrefixes, oldSets = self._delete(identifier)
        stamp = self._stamp()
        prefixes = set(prefix for prefix, schema, namespace in metadataFormats)
        prefixes.update(oldPrefixes)
        setSpecs = _flattenSetHierarchy((setSpec for setSpec, setName in sets))
        setSpecs.update(oldSets)
        self._add(stamp, identifier, setSpecs, prefixes)
        self._storeMetadataFormats(metadataFormats)

    def delete(self, identifier):
        oldPrefixes, oldSets = self._delete(identifier)
        if not oldPrefixes:
            return
        stamp = self._stamp()
        self._add(stamp, identifier, oldSets, oldPrefixes)
        self._tombStones.append(stamp)

    def oaiSelect(self, sets=[], prefix='oai_dc', continueAfter='0', oaiFrom=None, oaiUntil=None, batchSize='ignored'):
        start = max(int(continueAfter)+1, self._fromTime(oaiFrom))
        stop = self._untilTime(oaiUntil)
        stampIds = self._prefixes.get(prefix, [])
        if stop:
            stampIds = stampIds[bisect_left(stampIds,start):bisect_left(stampIds,stop)]
        else:
            stampIds = stampIds[bisect_left(stampIds,start):]
        if sets:
            allStampIdsFromSets = (self._sets.get(setSpec,[]) for setSpec in sets)
            stampIds = AndIterator(stampIds,
                reduce(OrIterator, allStampIdsFromSets))
        #WrapIterable to fool Observable's any message
        return WrapIterable((RecordId(self._getIdentifier(stampId), stampId) for stampId in stampIds))

    def getDatestamp(self, identifier):
        stamp = self.getUnique(identifier)
        if stamp == None:
            return None
        return strftime('%Y-%m-%dT%H:%M:%SZ', localtime(stamp/1000000.0))

    def getUnique(self, identifier):
        if hasattr(identifier, 'stamp'):
            return identifier.stamp
        return self._getStamp(identifier)

    def isDeleted(self, identifier):
        stamp = self.getUnique(identifier)
        if stamp == None:
            return False
        return stamp in self._tombStones

    def getAllMetadataFormats(self):
        return WrapIterable(self._getAllMetadataFormats())

    def getAllPrefixes(self):
        return self._prefixes.keys()

    def getSets(self, identifier):
        stamp = self.getUnique(identifier)
        if not stamp:
            return []
        return WrapIterable((setSpec for setSpec, stampIds in self._sets.items() if stamp in stampIds))

    def getPrefixes(self, identifier):
        stamp = self.getUnique(identifier)
        if not stamp:
            return []
        return WrapIterable((prefix for prefix, stampIds in self._prefixes.items() if stamp in stampIds))

    def getAllSets(self):
        return self._sets.keys()

    # private methods

    def _add(self, stamp, identifier, setSpecs, prefixes):
        for setSpec in setSpecs:
            self._getSetList(setSpec).append(stamp)
        for prefix in prefixes:
            self._getPrefixList(prefix).append(stamp)
        self._stamp2identifier[str(stamp)]=identifier

    def _getAllMetadataFormats(self):
        for prefix in self._prefixes.keys():
            schema = open(join(self._directory, 'prefixesInfo', '%s.schema' % escapeName(prefix))).read()
            namespace = open(join(self._directory, 'prefixesInfo', '%s.namespace' % escapeName(prefix))).read()
            yield (prefix, schema, namespace)

    def _getSetList(self, setSpec):
        if setSpec not in self._sets:
            filename = join(self._directory, 'sets', '%s.list' % escapeName(setSpec))
            self._sets[setSpec] = SortedFileList(filename, mergeTrigger=MERGE_TRIGGER)
        return self._sets[setSpec]

    def _getPrefixList(self, prefix):
        if prefix not in self._prefixes:
            filename = join(self._directory, 'prefixes', '%s.list' % escapeName(prefix))
            self._prefixes[prefix] = SortedFileList(filename, mergeTrigger=MERGE_TRIGGER)
        return self._prefixes[prefix]

    def _fromTime(self, oaiFrom):
        if not oaiFrom:
            return 0
        return int(mktime(strptime(oaiFrom, '%Y-%m-%dT%H:%M:%SZ'))*1000000.0)

    def _untilTime(self, oaiUntil):
        if not oaiUntil:
            return None
        UNTIL_IS_INCLUSIVE = 1 # Add one second to 23:59:59
        return int(mktime(strptime(oaiUntil, '%Y-%m-%dT%H:%M:%SZ'))*1000000.0) + UNTIL_IS_INCLUSIVE

    def _getIdentifier(self, stamp):
        return self._stamp2identifier.get(str(stamp), None)

    def _getStamp(self, identifier):
        result = self._stamp2identifier.getKeyFor(identifier)
        if result != None:
            result = int(result)
        return result

    def _delete(self, identifier):
        stamp = self.getUnique(identifier)
        stamp in self._tombStones and self._tombStones.remove(stamp)
        oldPrefixes = []
        oldSets = []
        if stamp != None:
            del self._stamp2identifier[str(stamp)]
            for prefix, prefixStamps in self._prefixes.items():
                if stamp in prefixStamps:
                    oldPrefixes.append(prefix)
                    prefixStamps.remove(stamp)
            for setSpec, setStamps in self._sets.items():
                if stamp in setStamps:
                    oldSets.append(setSpec)
                    setStamps.remove(stamp)
        return oldPrefixes, oldSets

    def _read(self):
        for prefix in (unescapeName(name[:-len('.list')]) for name in listdir(join(self._directory, 'prefixes')) if name.endswith('.list')):
            self._getPrefixList(prefix)
        for setSpec in (unescapeName(name[:-len('.list')]) for name in listdir(join(self._directory, 'sets')) if name.endswith('.list')):
            self._getSetList(setSpec)

    def _storeMetadataFormats(self, metadataFormats):
        for prefix, schema, namespace in metadataFormats:
            _write(join(self._directory, 'prefixesInfo', '%s.schema' % escapeName(prefix)), schema)
            _write(join(self._directory, 'prefixesInfo', '%s.namespace' % escapeName(prefix)), namespace)

    def _stamp(self):
        """time in microseconds"""
        return int(time()*1000000.0)

# helper methods

class RecordId(str):
    def __new__(self, identifier, stamp):
        return str.__new__(self, identifier)
    def __init__(self, identifier, stamp):
        self.stamp = stamp

def _writeLines(filename, lines):
    with open(filename + '.tmp', 'w') as f:
        for line in lines:
            f.write('%s\n' % line)
    rename(filename + '.tmp', filename)

def _write(filename, content):
    with open(filename + '.tmp', 'w') as f:
        f.write(content)
    rename(filename + '.tmp', filename)

def _flattenSetHierarchy(sets):
    """"[1:2:3, 1:2:4] => [1, 1:2, 1:2:3, 1:2:4]"""
    result = set()
    for setSpec in sets:
        parts = setSpec.split(':')
        for i in range(1, len(parts) + 1):
            result.add(':'.join(parts[:i]))
    return result

