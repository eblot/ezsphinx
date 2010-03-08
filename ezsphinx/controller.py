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

import codecs
import os
import util
from threading import Lock
from multiprocessing import Pool
from PyQt4.QtCore import QDir, QObject, pyqtSignal
from PyQt4.QtGui import QApplication, QMessageBox


def docutils_rest_to_html(rest):
    return util.docutils_rest_to_html(rest)
def sphinx_rest_to_html(rest, static_path=util.DEFAULT_STATIC_PATH):
    return util.sphinx_rest_to_html(rest, static_path)


class EzSphinxController(QObject):
    """Controller for the application"""
    
    postUpdate = pyqtSignal()
    
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
        self.postUpdate.connect(self._do_update)

    def quit(self):
        # terminate the pool's subprocess on our own, so that we can catch
        # any termination exception and discard it
        try:
            self._pool.terminate()
        except OSError:
            pass
        self._pool.join()

    def load_file(self, path):
        if QApplication.instance().rest.dirty:
            fn = QDir.convertSeparators(QApplication.instance().rest.filename)
            rc = QMessageBox.warning(QApplication.instance().mainwin, 
                    'EzSphinx', 'Save changes to %s before proceeding?' % fn,
                    QMessageBox.Discard|QMessageBox.Save|QMessageBox.Cancel)
            if rc == QMessageBox.Cancel:
                return False
            if rc == QMessageBox.Save:
                if not QApplication.instance().rest.save(fn):
                    return False
        QApplication.instance().rest.load(path)
        QApplication.instance().mainwin.update(('restedit', ))
       
    def set_rest(self, rest):
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
            QApplication.instance().warnreport.reset()
            for node in warning_nodes:
                try:
                    description = node.children[0].children[0] #.data
                except AttributeError, e:
                    print "Attribute Error: %s" % str(e)
                    continue
                QApplication.instance().warnreport.add(node.attributes['level'],
                                                       node.attributes['line'],
                                                       description)
            self._lock.acquire()
            self._html_docs.append(html)
            self._lock.release()
            self.postUpdate.emit()

    #-------------------------------------------------------------------------
    # Signal handlers (slots)
    #-------------------------------------------------------------------------

    def _do_update(self):
        """^: internal handler to refresh views asynchronously"""
        self._lock.acquire()
        html = self._html_docs.pop(0)
        self._lock.release()
        QApplication.instance().mainwin.render(html)
