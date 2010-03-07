========
EzSphinx
========

Overview
--------

EzSphinx_ aims at providing an interactive GUI editor to write 
reStructuredText_ and Sphinx_ documents and get near real-time WYSIWYG 
rendering.

For now, neither RestructuredText_ stylesheets nor actual Sphinx_ documents are 
actually supported.

Status
------

EzSphinx_ is a project in a very early stage of development. It should be seen 
as a proof of concept, not as a ready-to-use editor.

Never edit original documents: always **copy them first** before browsing and 
editing them within EzSphinx_. You've been warned.

Requirements
------------
 * Python_ 2.6+ (Python 3.x not supported yet)
 * PyQt_ 4.6+
 * docutils_ 0.6+
 * (Sphinx_)

.. _EzSphinx: http://github.com/eblot/ezsphinx/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _docutils: http://docutils.sourceforge.net/
.. _Python: http://www.python.org/
.. _Sphinx: http://sphinx.pocoo.org/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/

Thanks
------

EzSphinx has been initially based on the Enthought_ ReST editor.

It is loosely coupled with the original fork, as one of the major goal of 
EzSphinx_ is to keep the list of dependencies as small as possible. There is no
dependency on Enthought_ libraries.

.. _Enthought: http://www.enthought.com/
