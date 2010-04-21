/* begin license *
 *
 *     Meresco Components are components to build searchengines, repositories
 *     and archives, based on Meresco Core.
 *     Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
 *     Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
 *        http://www.kennisnetictopschool.nl
 *     Copyright (C) 2009 Delft University of Technology http://www.tudelft.nl
 *     Copyright (C) 2009 Tilburg University http://www.uvt.nl
 *     Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
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
#include <map>
#include <string>
#include <iterator>
#include "facetindex.h"
#include "docset.h"
#include "integerlist.h"
#include "triedict.h"
#include <org/apache/lucene/index/IndexReader.h>

using namespace org::apache;

#ifndef __docsetlist_h__
#define __docsetlist_h__

/**************** C++ implementation of DocSetList****************************/
typedef struct {
    char*   term;
    guint32 cardinality;
} cardinality_t;

typedef std::vector<cardinality_t> CardinalityList;
typedef std::vector<fwPtr> TermList;
typedef std::map<guint32, TermList> DocId2TermListMap;
typedef std::iterator<std::random_access_iterator_tag, guint32> Guint32Iterator;

class DocSetIterator;

class DocSetList : public std::vector<fwPtr> {
    private:
        guint32              _shadow;
        DocId2TermListMap    docId2TermList;
        TrieDict             dictionary;
    public:
        int measure(void) {
            const int allocOverhead = 16;
            int mysize = sizeof(this) + allocOverhead;
            for ( DocSetList::iterator i = begin(); i < end(); i++ ) {
                mysize += sizeof(fwPtr) + pDS(*i)->measure();
            }
            int mapNodeSize = sizeof(std::_Rb_tree_node_base);
            int mapSize = mapNodeSize * size() + allocOverhead;
            for ( DocId2TermListMap::iterator i = docId2TermList.begin(); i != docId2TermList.end(); i++ ) {
                mapSize += sizeof(guint32) + sizeof(TermList) + (*i).second.size() * sizeof(fwPtr);
            }
            int dictSize = dictionary.measure();
            return mysize + mapSize + dictSize;
        }
        DocSetList(int shadow): _shadow(shadow) {};
        ~DocSetList();
        void                 addDocSet(fwPtr docset, char *term);
        void                 merge(DocSetList* anotherlist);
        CardinalityList*     combinedCardinalities(DocSet* docset, guint32 maxResults, int doSort);
        DocSetList*          intersect(fwPtr docset);
        DocSetList*          termIntersect(DocSetList* rhs);
        fwPtr                innerUnion();
        CardinalityList*     jaccards(DocSet* docset, int minimum, int maximum, int totaldocs, int algorithm, int maxTermFreqPercentage);
        fwPtr                forTerm(char* term);
        int                  cardinalityForTerm(char* term);
        void                 removeDoc(guint32 doc);
        char*                getTermForDocset(DocSet *docset);
        char*                getTermForId(guint32 termId);
        bool                 cmpTerm(fwPtr lhs, fwPtr rhs);
        void                 sortOnTerm(void);
        void                 sortOnTermId(void);
        void                 docId2terms_add(guint32 docid, fwPtr docset);
        void                 nodecount(void);
        DocSetIterator       begin_docId(void);
        DocSetIterator       end_docId(void);
};


class DocSetIterator : public  Guint32Iterator {
    private:
        DocSetList::iterator _iter;
    public:
        DocSetIterator() {};
        DocSetIterator(DocSetList::iterator iter) : _iter(iter) {};
        DocSetIterator(const DocSetIterator& cp) : _iter(cp._iter) {};
        DocSetIterator& operator++() { _iter++; return *this; };
        guint32 operator-(DocSetIterator& rhs) { return _iter - rhs._iter; };
        DocSetIterator operator-(const guint32& rhs) {return DocSetIterator(_iter - rhs); };
        bool operator< (DocSetIterator& rhs) { return _iter <  rhs._iter; };
        bool operator>=(DocSetIterator& rhs) { return _iter >= rhs._iter; };
        bool operator<=(DocSetIterator& rhs) { return _iter <= rhs._iter; };
        DocSetIterator operator++(int n) {
            DocSetIterator result = *this;
            _iter.operator++(n);
            return result;
        };
        DocSetIterator operator--(int n) {
            DocSetIterator result = *this;
            _iter.operator--(n);
            return result;
        };
        void operator+=(int n) { _iter.operator+=(n); };

        guint32& operator*() { return pDS(*_iter)->_termOffset; };
};




/**************** C-interface for DocSetList ****************************/
extern "C" {
    int JACCARD_ONLY = 0;
    int JACCARD_MI = 1;
    int JACCARD_X2 = 2;
    DocSetList*      DocSetList_create               (void);
    int              DocSetList_measure              (DocSetList* list);
    void             DocSetList_add                  (DocSetList* list, fwPtr docset, char* term);
    void             DocSetList_merge                (DocSetList* list, DocSetList* anotherlist);
    void             DocSetList_removeDoc            (DocSetList* list, guint32 doc);
    int              DocSetList_size                 (DocSetList* list);
    fwPtr            DocSetList_get                  (DocSetList* list, int i);
    fwPtr            DocSetList_getForTerm           (DocSetList* list, char* term);
    int              DocSetList_cardinalityForTerm   (DocSetList* list, char* term);
    CardinalityList* DocSetList_combinedCardinalities(DocSetList* list, fwPtr docset, guint32 maxResults, int doSort);
    DocSetList*      DocSetList_intersect            (DocSetList* list, fwPtr docset);
    DocSetList*      DocSetList_termIntersect        (DocSetList* self, DocSetList* rhs);
    fwPtr            DocSetList_innerUnion           (DocSetList* self);
    CardinalityList* DocSetList_jaccards             (DocSetList* list, fwPtr docset, int minimum, int maximum, int totaldocs, int algorithm, int maxTermFreqPercentage);
    void             DocSetList_delete               (DocSetList* list);
    void             DocSetList_sortOnCardinality    (DocSetList* list);
    void             DocSetList_sortOnTerm           (DocSetList* list);
    void             DocSetList_sortOnTermId         (DocSetList* list);
    DocSetList*      DocSetList_forField             (lucene::index::IndexReader* indexReader, char* fieldname, IntegerList*);
    void             DocSetList_printMemory          (DocSetList* list);
    char*            DocSetList_getTermForDocset     (DocSetList* list, fwPtr docset);
    void             DocSetList_docId2terms_add      (DocSetList* list, guint32 docid, fwPtr docset);

    cardinality_t*   CardinalityList_at              (CardinalityList* vector, int i);
    int              CardinalityList_size            (CardinalityList* vector);
    void             CardinalityList_free            (CardinalityList* vector);

}

#endif

