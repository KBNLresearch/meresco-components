/* begin license *
 *
 *     Meresco Components are components to build searchengines, repositories
 *     and archives, based on Meresco Core.
 *     Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
 *     Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
 *        http://www.kennisnetictopschool.nl
 *     Copyright (C) 2009 Delft University of Technology http://www.tudelft.nl
 *     Copyright (C) 2009 Tilburg University http://www.uvt.nl
 *     Copyright (C) 2007-2009 Seek You Too (CQ2) http://www.cq2.nl
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
#include <Python.h>
#include <vector>
#include <map>
#include <string>
#include "facetindex.h"
#include "docset.h"
#include "integerlist.h"
#include "triedict.h"

#ifndef __docsetlist_h__
#define __docsetlist_h__

/**************** C++ implementation of DocSetList****************************/
typedef struct {
    char*   term;
    guint32 cardinality;
} cardinality_t;

typedef std::vector<cardinality_t> CardinalityList;
typedef std::vector<fwPtr> TermList;

class DocSetList : public std::vector<fwPtr> {
    private:
        std::map<guint32, TermList> docId2TermList;
        TrieDict             dictionary;
    public:
        ~DocSetList();
        void                 addDocSet(fwPtr docset, char *term);
        CardinalityList*     combinedCardinalities(DocSet* docset, guint32 maxResults, int doSort);
        DocSetList*          intersect(DocSet* docset); 
        CardinalityList*     jaccards(DocSet* docset, int minimum, int maximum, int totaldocs, int algorithm);
        fwPtr                forTerm(char* term);
        void                 removeDoc(guint32 doc);
        char*                getTermForDocset(DocSet *docset);
        bool                 cmpTerm(fwPtr lhs, fwPtr rhs);
        void                 sortOnTerm(void);
        void                 docId2terms_add(guint32 docid, fwPtr docset);
        void                 nodecount(void);
};

/**************** C-interface for DocSetList ****************************/
extern "C" {
    int JACCARD_ONLY = 0;
    int JACCARD_MI = 1;
    int JACCARD_X2 = 2;
    DocSetList*      DocSetList_create               (void);
    void             DocSetList_add                  (DocSetList* list, fwPtr docset, char* term);
    void             DocSetList_removeDoc            (DocSetList* list, guint32 doc);
    int              DocSetList_size                 (DocSetList* list);
    fwPtr            DocSetList_get                  (DocSetList* list, int i);
    fwPtr            DocSetList_getForTerm           (DocSetList* list, char* term);
    CardinalityList* DocSetList_combinedCardinalities(DocSetList* list, fwPtr docset, guint32 maxResults, int doSort);
    DocSetList* DocSetList_intersect(DocSetList* list, fwPtr docset);
    CardinalityList* DocSetList_jaccards             (DocSetList* list, fwPtr docset, int minimum, int maximum, int totaldocs, int algorithm);
    void             DocSetList_delete               (DocSetList* list);
    void             DocSetList_sortOnCardinality    (DocSetList* list);
    void             DocSetList_sortOnTerm           (DocSetList* list);
    DocSetList*      DocSetList_fromTermEnum         (PyJObject* termEnum, PyJObject* termDocs, IntegerList *);
    void             DocSetList_printMemory          (DocSetList* list);
    char*            DocSetList_getTermForDocset     (DocSetList* list, fwPtr docset);
    void             DocSetList_docId2terms_add      (DocSetList* list, guint32 docid, fwPtr docset);

    cardinality_t*   CardinalityList_at              (CardinalityList* vector, int i);
    int              CardinalityList_size            (CardinalityList* vector);
    void             CardinalityList_free            (CardinalityList* vector);

}

#endif


