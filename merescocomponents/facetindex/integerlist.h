/* begin license *
 *
 *     Meresco Components are components to build searchengines, repositories
 *     and archives, based on Meresco Core.
 *     Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
 *     Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
 *     Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
 *        http://www.kennisnetictopschool.nl
 *
 *     This file is part of Meresco Components.
 *
 *     Meresco Components is free software; you can redistribute it and/or modify
 *     it under the terms of the GNU General Public License as published by
 *     the Free Software Foundation; either version 2 of the License, or
 *     (at your option) any later version.
 *
 *     Meresco Components is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *     GNU General Public License for more details.
 *
 *     You should have received a copy of the GNU General Public License
 *     along with Meresco Components; if not, write to the Free Software
 *     Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * end license */
#include <vector>

#include <glib.h>

#ifndef __integerlist_h__
#define __integerlist_h__

class IntegerList : public std::vector<guint32> {
    public:
        IntegerList(int n);
        IntegerList(std::vector<guint32>::iterator first, std::vector<guint32>::iterator last) : std::vector<guint32>(first, last) {}
        void append(guint32);
        IntegerList* slice(int, int, int);
        int mergeFromOffset(int);
        int save(char* filename, int offset);
        int extendFrom(char* filename);
        int extendTo(char* filename);
};

extern "C" {
    IntegerList*    IntegerList_create               (int n);
    void            IntegerList_delete               (IntegerList*);
    void            IntegerList_append               (IntegerList*, guint32);
    int             IntegerList_size                 (IntegerList*);
    guint32         IntegerList_get                  (IntegerList*, int);
    void            IntegerList_set                  (IntegerList*, int, guint32);
    IntegerList*    IntegerList_slice                (IntegerList*, int, int, int);
    void            IntegerList_delitems             (IntegerList* list, int start, int stop);
    int             IntegerList_mergeFromOffset      (IntegerList* list, int);
    int             IntegerList_save                 (IntegerList* list, char* filename, int offset);
    int             IntegerList_extendFrom           (IntegerList* list, char* filename);
    int             IntegerList_extendTo             (IntegerList* list, char* filename);
}

#endif


