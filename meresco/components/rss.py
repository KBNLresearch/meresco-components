## begin license ##
#
#    Meresco Components are components to build searchengines, repositories
#    and archives, based on Meresco Core.
#    Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2007 SURFnet. http://www.surfnet.nl
#    Copyright (C) 2011 Stichting Kennisnet http://www.kennisnet.nl
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

from xml.sax.saxutils import escape as xmlEscape
from xml.sax import SAXParseException

from cgi import parse_qs
from urlparse import urlsplit

from amara.binderytools import bind_string

from meresco.core import Observable
from meresco.components.sru.sruparser import SruMandatoryParameterNotSuppliedException
from meresco.components.http import utils as httputils

from cqlparser.cqlparser import parseString as CQLParseException
from meresco.components.web import WebQuery

from weightless.core import compose

class BadRequestException(Exception):
    pass

class Rss(Observable):

    def __init__(self, title, description, link, antiUnaryClause='', **sruArgs):
        Observable.__init__(self)
        self._title = title
        self._description = description
        self._link = link
        self._antiUnaryClause = antiUnaryClause
        self._sortKeys = sruArgs.get('sortKeys', None)
        self._maximumRecords = sruArgs.get('maximumRecords', 10)

    def handleRequest(self, RequestURI='', **kwargs):
        yield httputils.okRss
        yield """<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>"""
        try:
            Scheme, Netloc, Path, Query, Fragment = urlsplit(RequestURI)
            arguments = parse_qs(Query)
            sortKeys = arguments.get('sortKeys', [self._sortKeys])[0]
            sortBy, sortDescending = None, None
            if sortKeys:
                sortBy, ignored, sortDescending = sortKeys.split(',')
                sortDescending = sortDescending == '1'

            maximumRecords = int(arguments.get('maximumRecords', [self._maximumRecords])[0])
            query = arguments.get('query', [''])[0]
            filters = arguments.get('filter', [])
            startRecord = 1

            if not query and not self._antiUnaryClause:
                raise SruMandatoryParameterNotSuppliedException("query")
            webquery = WebQuery(query, antiUnaryClause=self._antiUnaryClause)
            for filter in filters:
                if not ':' in filter:
                    raise BadRequestException('Invalid filter: %s' % filter) 
                field,term = filter.split(':', 1)
                webquery.addFilter(field, term)

            cqlAbstractSyntaxTree = webquery.ast
        except (SruMandatoryParameterNotSuppliedException, BadRequestException, CQLParseException), e:
            yield '<title>ERROR %s</title>' % xmlEscape(self._title)
            yield '<link>%s</link>' % xmlEscape(self._link)
            yield "<description>An error occurred '%s'</description>" % xmlEscape(str(e))
            yield """</channel></rss>"""
            raise StopIteration()

        yield '<title>%s</title>' % xmlEscape(self._title)
        yield '<description>%s</description>' % xmlEscape(self._description)
        yield '<link>%s</link>' % xmlEscape(self._link)

        SRU_IS_ONE_BASED = 1 #And our RSS plugin is closely based on SRU
        for data in compose(self._yieldResults(
                cqlAbstractSyntaxTree=cqlAbstractSyntaxTree,
                start=startRecord - SRU_IS_ONE_BASED,
                stop=startRecord - SRU_IS_ONE_BASED+maximumRecords,
                sortBy=sortBy,
                sortDescending=sortDescending )):
            yield data

        yield """</channel>"""
        yield """</rss>"""

    def _yieldResults(self, cqlAbstractSyntaxTree=None, start=0, stop=9, sortBy=None, sortDescending=False, **kwargs):
        total, hits = self.any.executeCQL(
            cqlAbstractSyntaxTree=cqlAbstractSyntaxTree,
            start=start,
            stop=stop,
            sortBy=sortBy,
            sortDescending=sortDescending,
            **kwargs
        )

        for recordId in hits:
            yield self.any.getRecord(recordId)
