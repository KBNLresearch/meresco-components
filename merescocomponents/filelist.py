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
from os import rename, stat
from os.path import isfile
from bisect import bisect_left
from packer import IntPacker

class FileList(object):
    def __init__(self, filename, initialContent=[], packer=IntPacker()):
        self._filename = filename
        self._packer = packer
        isfile(filename) or open(self._filename, 'w')
        self._length = stat(self._filename).st_size/self._packer.length
        if initialContent:
            self._writeInitialContent(initialContent)
        self._file = open(self._filename, 'ab+')

    def _writeInitialContent(self, initialContent):
        with open(self._filename+'~', 'wb') as self._file:
            self._length = 0
            for item in initialContent:
                self._appendToopen(item)
        rename(self._filename+'~',self._filename)

    def append(self, item):
        self._appendToopen(item)

    def __iter__(self):
        for i in xrange(self._length):
            yield self[i]

    def close(self):
        if self._file != None:
            self._file.close()

    def _appendToopen(self, item):
        self._file.seek(self._length * self._packer.length)
        self._file.write(self._packer.pack(item))
        self._file.flush()
        self._length += 1

    def __len__(self):
        return self._length

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._slice(index)
        if index < 0:
            index = self._length + index
        if 0 <= index < self._length:
            self._file.seek(index * self._packer.length)
            return self._packer.unpack(self._file.read(self._packer.length))
        raise IndexError('list index out of range')

    def _slice(self, aSlice):
        return self.FileListSeq(self, *_sliceWithinRange(aSlice, self._length))

    class FileListSeq(object):
        def __init__(self, mainList, start, stop, step):
            self._mainList = mainList
            self._start = start
            self._stop = stop
            self._step = step

        def __iter__(self):
            for i in range(self._start, self._stop, self._step):
                yield self._mainList[i]

        def __getitem__(self, index):
            if isinstance(index, slice):
                start,stop, step = _sliceWithinRange(index, len(self))
                nStart = self._start + start * self._step
                nStop = self._start + stop * self._step
                nStep = self._step * step
                return self.__class__(self._mainList, nStart, nStop, nStep)
            return self._mainList[self._start + index*self._step]

        def __len__(self):
            return abs((self._start - self._stop)/self._step)

class SortedFileList(FileList):
    def __contains__(self, item):
        position = bisect_left(self, item)
        return position < self._length and item == self[position]

    def append(self, item):
        if len(self) > 0 and item <= self[-1]:
            raise ValueError('%s should be greater than %s', (item, self[-1]))
        FileList.append(self, item)
    

def _sliceWithinRange(aSlice, listLength):
        start = aSlice.start or 0
        stop = aSlice.stop or listLength
        step = aSlice.step or 1
        if stop < 0:
            stop += listLength
        if stop > listLength:
            stop = listLength
        if start < 0:
            start += listLength
        if start < 0:
            start = 0
        if step < 0:
            start,stop = stop-1, start-1
        return start, stop, step
