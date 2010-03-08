#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# ezSphinx
#   A interactive PyQT-based editor for Restructured Text documentation tool
#
# Copyright (C) 2010 Emmanuel Blot <emmanuel.blot@free.fr>
# This software is provided without warranty under the terms of the BSD
# license.
#
# Based on work done by Evan Patterson (BSD license)
#   Copyright (c) 2009, Enthought, Inc.
# See ezsphinx/util.py for details
#-----------------------------------------------------------------------------


from setuptools import setup, find_packages
import sys

setup_extras = {}

# is there a better way to specify py2app options ?
if 'py2app' in sys.argv:
    # py2app for Mac OS X application package
    setup_extras.update({
        'app': ['ezsphinx/ezsphinx.py'],
        'data_files': ['--iconfile', 'ezsphinx/images/sphinx.icns'],
        'options': {'py2app': {'argv_emulation': True}},
        'setup_requires': ['py2app']
    })

setup (
    name = 'ezSphinx',
    version = '0.1.4',
    description = 'Interactive editor for Rst and Sphinx documentation tools',
    author = 'Emmanuel Blot',
    author_email = 'emmanuel.blot@free.fr',
    license = 'BSD',
    keywords = 'docutils pyqt qt rst sphinx editor',
    url = 'http://github.com/eblot/ezsphinx/',

    install_requires = [ 
        'docutils>=0.6',
        # can't make it work, I'm fed up with setuptools...
        'sip>=4.9',
        'pyqt>=4.6', 
    ],

    zip_safe = True,
    
    packages = find_packages(),
    
    entry_points = {
        # Comment the following entry to generate a standard EGG file
        'setuptools.installation': [ 
            'eggsecutable = ezsphinx.ezsphinx:main', 
        ],
    },

    **setup_extras
)
