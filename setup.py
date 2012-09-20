#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-
## begin license ##
# 
# "Meresco Components" are components to build searchengines, repositories
# and archives, based on "Meresco Core". 
# 
# Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2009-2010 Delft University of Technology http://www.tudelft.nl
# Copyright (C) 2009 Tilburg University http://www.uvt.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012 Stichting Bibliotheek.nl (BNL) http://stichting.bibliotheek.nl
# 
# This file is part of "Meresco Components"
# 
# "Meresco Components" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "Meresco Components" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "Meresco Components"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##

from distutils.core import setup
from distutils.extension import Extension

setup(
    name = 'meresco-components',
    packages = [
        'meresco.components',
        'meresco.components.autocomplete',
        'meresco.components.cql',
        'meresco.components.drilldown',
        'meresco.components.facetindex',
        'meresco.components.http',
        'meresco.components.log',
        'meresco.components.msgbox',
        'meresco.components.ngram',
        'meresco.components.numeric',
        'meresco.components.sru',
        'meresco.components.web',
        'meresco.components.xml_generic',
    ],
    package_data={
        'meresco.components': ['rules/*.rules'],
        'meresco.components.autocomplete': ['files/*.js', 'files/*.css'],
        'meresco.components.xml_generic': [
            'schemas/*',
            'schemas-lom/*.xsd',
            'schemas-lom/common/*',
            'schemas-lom/examples/*',
            'schemas-lom/extend/*',
            'schemas-lom/unique/*',
            'schemas-lom/vocab/*'
        ]
    },
    ext_modules = [
        Extension("meresco.components.facetindex._facetindex", [
                      'meresco/components/facetindex/_integerlist.cpp',
                  ],
                  extra_compile_args = [
                      '-g', 
                      '-O3'
                  ],
        )
    ],
    version = '%VERSION%',
    url = 'http://seecr.nl',
    author = 'Seecr (Seek You Too B.V.)',
    author_email = 'info@seecr.nl',
    description = 'Meresco Components are components to build search engines and archives, based on Meresco Core.',
    long_description = 'Meresco Components are components to build search engines and archives, based on Meresco Core.',
    license = 'GPL',
    platforms = 'all',
)
