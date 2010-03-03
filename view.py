# import sys
from PyQt4 import QtCore, QtGui, QtWebKit
from gui import Ui_MainWindow
import os
import tempfile
import threading
# import codecs
# from os.path import isfile


class WarningReportView(QtGui.QTableView):
    """
    """

    def __init__(self, view): 
        QtGui.QTableView.__init__(self) 
        self._parentview = view
        font = QtGui.QFont()
        font.setPointSize(10)
        self.setFont(font)
        font = QtGui.QFont()
        font.setWeight(QtGui.QFont.Bold)
        self.setAlternatingRowColors(True)
        header = self.horizontalHeader()
        header.setFont(font) 
        header.setStretchLastSection(True)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def currentChanged(self, current, previous):
        row = current.row()
        line = self.model().get_line(row)
        self._parentview.select_line(line)

    def refresh(self):
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeRowsToContents()


class ESphinxView(QtGui.QMainWindow):
    """
    """
    
    COLORS = 'green yellow blue red'.split()
    
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
        self._ui.textedit.textChanged.connect(self._textedit_update)
        self._ui.textedit.blockCountChanged.connect(self._blockcount_update)
        QtCore.QObject.connect(self, QtCore.SIGNAL("_reload()"), self._reload)
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
        self._warnreportview = WarningReportView(self)
        self._ui.tablelayout.addWidget(self._warnreportview)
        self._ui.menubar.setNativeMenuBar(True)
        # file_menu = self._ui.menubar.addMenu(self.tr("&File"));
        self._formats = {}
        self._last_text_len = 0
        self._last_warnings = {}

    def set_model(self, model):
        self._model = model
        self._warnreportview.setModel(model.get_warnreport())

    def _textedit_update(self):
        # Ok, so textChanged is stupid, as it gets signalled when *text*
        # is not changed but formatting is. So we need to discriminate from
        # both kind of calls...
        text = self._ui.textedit.toPlainText()
        if len(text) != self._last_text_len:
            self._last_text_len = len(text)
            self._model.update_rest(text)
    
    def _blockcount_update(self, newcount):
        self._update_line()

    def _reload(self):
        self._lock.acquire()
        doc = self._docs.pop(0)
        self._lock.release()
        self._ui.webview.setHtml(doc)
        self._warnreportview.refresh()
        self._update_background()
    
    def _generate_formats(self):
        if self._formats:
            return
        textedit = self._ui.textedit
        format = textedit.document().findBlock(0).blockFormat()
        self._formats[0] = format
        for lvl,color in enumerate(self.COLORS):
            format = QtGui.QTextBlockFormat(format)
            brush = QtGui.QBrush(QtGui.QColor(color))
            format.setBackground(brush)
            self._formats[lvl+1] = format.toBlockFormat()

    def refresh(self):
        # called from a worker thread, need to dispath the event with the
        # help of a slot/signal
        self._lock.acquire()
        self._docs.append(self._model.get_html())
        self._lock.release()
        self.emit(QtCore.SIGNAL('_reload()'))

    def select_line(self, line):
        lineColor = QtGui.QColor(QtCore.Qt.gray).lighter(150)
        selection = QtGui.QTextEdit.ExtraSelection()
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, 
                                     True)
        textedit = self._ui.textedit
        cursor = textedit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start, 
                            QtGui.QTextCursor.MoveAnchor, 1)
        cursor.movePosition(QtGui.QTextCursor.Down, 
                            QtGui.QTextCursor.MoveAnchor, line-1)
        selection.cursor = cursor
        selection.cursor.clearSelection()
        textedit.setTextCursor(cursor)
        extraSelections = []
        extraSelections.append(selection)
        textedit.setExtraSelections(extraSelections)
        
    def _update_background(self):
        lines = self._model.get_warnreport().get_lines()
        warnings = self.differentiate(self._last_warnings, lines) 
        self._last_warnings = lines

        if not self._formats:
            self._generate_formats()
        textedit = self._ui.textedit

        # could be optmized to move only once
        for line in sorted(warnings):
            print "LINE %d" % line
            level = warnings[line]
            line = line-1
            # start setting new background color
            cursor = textedit.textCursor()
            #print "A (%d,%d)" % (cursor.blockNumber(), cursor.columnNumber()),
            cursor.movePosition(QtGui.QTextCursor.Start, 
                                QtGui.QTextCursor.MoveAnchor, 1)
            #print "B (%d,%d)" % (cursor.blockNumber(), cursor.columnNumber()),
            cursor.movePosition(QtGui.QTextCursor.Down, 
                                QtGui.QTextCursor.MoveAnchor, line)
            print "C (%d,%d)" % (cursor.blockNumber(), cursor.columnNumber()),
            cursor.setBlockFormat(self._formats[level])
            # stop setting new background color, only if there a next block
            # if no block existed after the current block, the current block
            # would be updated with the default format
            move = cursor.movePosition(QtGui.QTextCursor.Down,
                                       QtGui.QTextCursor.MoveAnchor, 1)
            print "D (%d,%d)" % (cursor.blockNumber(), cursor.columnNumber())
            if move:
                cursor.setBlockFormat(self._formats[0])
    
    def _update_line(self):
        if not self._formats:
            self._generate_formats()
        textedit = self._ui.textedit
        cursor = textedit.textCursor()
        line = cursor.blockNumber()
        lines = filter(lambda x: x>0, [line, line+1])
        for line in lines:
            level = line in self._last_warnings and \
                self._last_warnings[line] or 0
            cursor.movePosition(QtGui.QTextCursor.StartOfBlock,
                                QtGui.QTextCursor.MoveAnchor, 1)
            print "X (%d,%d)" % (cursor.blockNumber(), cursor.columnNumber()),
            cursor.setBlockFormat(self._formats[level])
            # stop setting new background color, only if there a next block
            # if no block existed after the current block, the current block
            # would be updated with the default format
            move = cursor.movePosition(QtGui.QTextCursor.Down, 
                                       QtGui.QTextCursor.MoveAnchor, 1)
            print "Y (%d,%d)" % (cursor.blockNumber(), cursor.columnNumber())
            if move:
                line += 1
                level = line in self._last_warnings and \
                    self._last_warnings[line] or 0
                cursor.setBlockFormat(self._formats[level])

    @staticmethod
    def differentiate(old, new):
        sold = set(old)
        snew = set(new)
        mark, sweep = snew.difference(sold), sold.difference(snew)
        dwarn = {}
        for m in mark:
            dwarn[m] = new[m]
        for s in sweep:
            dwarn[s] = 0
        return dwarn