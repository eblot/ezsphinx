# import sys
from PyQt4 import QtCore, QtGui, QtWebKit
from ui import Ui_MainWindow
import os
import tempfile
import threading
# import codecs
# from os.path import isfile

class ESphinxView(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._model = None
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        #self.watcher = QtCore.QFileSystemWatcher(self)
        #QtCore.QObject.connect(self.ui.button_open,QtCore.SIGNAL("clicked()"), self.file_dialog)
        #QtCore.QObject.connect(self.ui.button_save,QtCore.SIGNAL("clicked()"), self.file_save)
        #QtCore.QObject.connect(self.ui.editor_window,QtCore.SIGNAL("textChanged()"), self.enable_save)
        #QtCore.QObject.connect(self.watcher,QtCore.SIGNAL("fileChanged(const QString&)"), self.file_changed)
        #self.filename = False
        QtCore.QObject.connect(self._ui.textedit,
                               QtCore.SIGNAL("textChanged()"), 
                               self._textedit_update) 
        QtCore.QObject.connect(self,
                               QtCore.SIGNAL("_reload()"), 
                               self._reload)
        self._lock = threading.Lock()
        self._docs = []
        font = QtGui.QFont()
        font.setFamily("Monaco")
        font.setPointSize(10)
        self._ui.textedit.setFont(font)
    
    def connect(self, model):
        self._model = model

    def _textedit_update(self):
        if self._model:
            self._model.update_rest(self._ui.textedit.toPlainText())

    def _reload(self):
        self._lock.acquire()
        doc = self._docs.pop(0)
        self._lock.release()
        self._ui.webview.setHtml(doc)

    def refresh(self):
        # called from a worker thread, need to dispath the event with the
        # help of a slot/signal
        self._lock.acquire()
        self._docs.append(self._model.get_html())
        self._lock.release()
        self.emit(QtCore.SIGNAL('_reload()'))
