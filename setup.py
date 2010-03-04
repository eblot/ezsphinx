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

setup(
    name = 'ezSphinx',
    version = '0.1',
    description = 'Interactive editor for Rst and Sphinx documentation tools',
    author = 'Emmanuel Blot',
    author_email = 'emmanuel.blot@free.fr',
    license = 'BSD',
    keywords = 'docutils pyqt qt rst sphinx editor',
    # url = '',

    install_requires = [ 
        'docutils>=0.6', 
        'pyqt>=4.6' 
    ],

    zip_safe = True,
    
    packages = find_packages(),
    
    entry_points = {
        # Comment the following entry to generate a standard EGG file
        'setuptools.installation': [ 
            'eggsecutable = ezsphinx.ezsphinx:main', 
        ],
    }
)
