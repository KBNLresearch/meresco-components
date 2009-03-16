## begin license ##
#
#    Meresco Components are components to build searchengines, repositories
#    and archives, based on Meresco Core.
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2009 Delft University of Technology http://www.tudelft.nl
#    Copyright (C) 2009 Tilburg University http://www.uvt.nl
#    Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
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

from libfacetindex import libFacetIndex
from ctypes import POINTER
from cq2utils import deallocator

TRIEDICT = POINTER(None)

TrieDict_create = libFacetIndex.TrieDict_create
TrieDict_create.argtypes = []
TrieDict_create.restype = TRIEDICT

TrieDict_delete = libFacetIndex.TrieDict_delete
TrieDict_delete.argtypes = [TRIEDICT]
TrieDict_delete.restype = None


class TrieDict(object):
    def __init__(self):
        self._cobj = TrieDict_create()
        self._dealloc = deallocator(TrieDict_delete, self._cobj)
        self._as_parameter_ = self._cobj
        