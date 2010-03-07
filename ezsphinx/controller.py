#-----------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
# 
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#  
#  Author: Evan Patterson
#  Date:   06/18/2009
#
#-----------------------------------------------------------------------------

# Standard library imports
import codecs
import os
import util
from threading import Lock
from multiprocessing import Pool
from PyQt4.QtCore import QObject, SIGNAL

from model import EzSphinxRestModel, WarningReportModel, FileTreeModel
from view import EzSphinxWindow

def docutils_rest_to_html(rest):
    return util.docutils_rest_to_html(rest)
def sphinx_rest_to_html(rest, static_path=util.DEFAULT_STATIC_PATH):
    return util.sphinx_rest_to_html(rest, static_path)


class EzSphinxController(QObject):
    """Controller for the application"""
    
    def __init__(self, parent):
        QObject.__init__(self, parent)
        self._rstsrc = ''
        self.use_sphinx = False
        self.sphinx_static_path = ''
        self.save_html = False
        self.html_filepath = ''
        self._pool = None
        self._processing = False
        self._queued = False
        self._pool = Pool(processes=1)
        self._lock = Lock()
        self._html_docs = []
        QObject.connect(self, SIGNAL("_do_update()"), self._do_update)

    @property
    def warnreport(self):
        return self._warnreport
    
    @property
    def filetree(self):
        return self._filetree

    @property
    def rest(self):
        return self._rest
    
    def run(self):
        self._rest = EzSphinxRestModel()
        self._warnreport = WarningReportModel()
        self._filetree = FileTreeModel()
        self._window = EzSphinxWindow()
        self._window.show()

    def quit(self):
        # terminate the pool's subprocess on our own, so that we can catch
        # any termination exception and discard it
        try:
            self._pool.terminate()
        except OSError:
            pass
        self._pool.join()

    def load_file(self, path):
        if self._rest.replace(path):
            self._window.update_rest()
        
    def update_rest(self, rest):
        self._rstsrc = rest
        self._queue_html()
    
    def _queue_html(self):
        if self._processing:
            self._queued = True
        else:
            self._processing = True
            self._gen_html()
            
    def _gen_html(self):
        args = [ self._rstsrc ]
        if self.use_sphinx:
            func = sphinx_rest_to_html
            if self.sphinx_static_path:
                args.append(self.sphinx_static_path)
        else:
            func = docutils_rest_to_html
        self._pool.apply_async(func, args, callback=self._set_html)

    def _set_html(self, result):
        if self._queued:
            self._gen_html()
            self._queued = False
        else:
            self._processing = False
            html, warning_nodes = result[0].decode('utf-8'), result[1]
            self._warnreport.reset()
            for node in warning_nodes:
                try:
                    description = node.children[0].children[0] #.data
                except AttributeError, e:
                    print "Attribute Error: %s" % str(e)
                    continue
                self._warnreport.add(node.attributes['level'],
                                     node.attributes['line'],
                                     description)
            self._lock.acquire()
            self._html_docs.append(html)
            self._lock.release()
            self.emit(SIGNAL('_do_update()'))

    #-------------------------------------------------------------------------
    # Signal handlers (slots)
    #-------------------------------------------------------------------------

    def _do_update(self):
        """^: internal handler to refresh the textedit content asynchronously"""
        self._lock.acquire()
        html = self._html_docs.pop(0)
        self._lock.release()
        self._window.render(html)
