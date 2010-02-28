# import sys
from PyQt4 import QtCore, QtGui, QtWebKit
from gui import Ui_MainWindow
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
        font.setPointSize(11)
        self._ui.textedit.setFont(font)
        self._ui.webview.setTextSizeMultiplier(0.8)
        self._ui.hlayout.setContentsMargins(4,4,4,0)
        self._ui.vlayout.setContentsMargins(4,0,4,0)
        self._ui.textlayout.setContentsMargins(0,0,2,0)
        self._ui.weblayout.setContentsMargins(2,0,2,2)
        self._ui.tablelayout.setContentsMargins(4,0,4,0)
        self._warnreportview = WarningReportView()
        self._ui.tablelayout.addWidget(self._warnreportview)

    def set_model(self, model):
        self._model = model
        self._warnreportview.setModel(model.get_warnreport())

    def _textedit_update(self):
        if self._model:
            self._model.update_rest(self._ui.textedit.toPlainText())

    def _reload(self):
        self._lock.acquire()
        doc = self._docs.pop(0)
        self._lock.release()
        self._ui.webview.setHtml(doc)
        self._warnreportview.refresh()

    def refresh(self):
        # called from a worker thread, need to dispath the event with the
        # help of a slot/signal
        self._lock.acquire()
        self._docs.append(self._model.get_html())
        self._lock.release()
        self.emit(QtCore.SIGNAL('_reload()'))


class WarningReportView(QtGui.QTableView):
    """
    """

    def __init__(self, *args): 
        QtGui.QTableView.__init__(self, *args) 
        font = QtGui.QFont()
        font.setPointSize(10)
        self.setFont(font)
        font = QtGui.QFont()
        font.setWeight(QtGui.QFont.Bold)
        self.setAlternatingRowColors(True)
        header = self.horizontalHeader()
        header.setFont(font) 
        header.setStretchLastSection(True)

    def refresh(self):
        self.resizeRowsToContents()
