# import sys
from PyQt4 import QtCore, QtGui, QtWebKit
from ConfigParser import SafeConfigParser as ConfigParser
from gui import Ui_MainWindow
from binascii import hexlify, unhexlify
import os
import tempfile
import time 
import threading
# import codecs
# from os.path import isfile

class EasyConfigParser(ConfigParser):
    """Simplify defaut configuration"""
    
    def get(self, section, option, default=None):
        if not self.has_section(section):
            return default
        if not self.has_option(section, option):
            return default
        return ConfigParser.get(self, section, option)

    def set(self, section, option, value):
        if not self.has_section(section):
            self.add_section(section)
        ConfigParser.set(self, section, option, str(value))

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
        self._parentview.set_focus_textedit()

    def refresh(self):
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeRowsToContents()


class ESphinxView(QtGui.QMainWindow):
    """
    """
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._model = None
        ui = Ui_MainWindow()
        self._ui = ui
        ui.setupUi(self)
        #self.watcher = QtCore.QFileSystemWatcher(self)
        #QtCore.QObject.connect(self.ui.button_open,QtCore.SIGNAL("clicked()"), self.file_dialog)
        #QtCore.QObject.connect(self.ui.button_save,QtCore.SIGNAL("clicked()"), self.file_save)
        #QtCore.QObject.connect(self.ui.editor_window,QtCore.SIGNAL("textChanged()"), self.enable_save)
        #QtCore.QObject.connect(self.watcher,QtCore.SIGNAL("fileChanged(const QString&)"), self.file_changed)
        #self.filename = False
        ui.textedit.textChanged.connect(self._textedit_update)
        ui.textedit.blockCountChanged.connect(self._blockcount_update)
        QtCore.QObject.connect(self, QtCore.SIGNAL("_reload()"), self._reload)
        self._lock = threading.Lock()
        self._docs = []

        ui.webview.setTextSizeMultiplier(0.8)
        ui.ftlayout.setContentsMargins(0,4,1,0)
        ui.elayout.setContentsMargins(1,4,1,0)
        ui.vlayout.setContentsMargins(4,0,4,0)
        ui.textlayout.setContentsMargins(0,0,2,0)
        ui.weblayout.setContentsMargins(1,0,2,2)
        ui.tablelayout.setContentsMargins(1,0,2,0)
        self._warnreportview = WarningReportView(self)
        ui.tablelayout.addWidget(self._warnreportview)
        ui.menubar.setNativeMenuBar(True)
        # file_menu = ui.menubar.addMenu(self.tr("&File"));

        filetree = ui.filetree
        filetree.setSortingEnabled(True)
        #self.tree.hideColumn(1)
        filetree.setColumnWidth(0, 50)
        # ui.filetree.show()
        font = filetree.font()
        font.setPointSize(10)
        filetree.setFont(font)
        filetree.setHeaderHidden(True)
        filetree.clicked.connect(self._select_file)

        keyseq = QtGui.QKeySequence("Ctrl+T")
        shortcut = QtGui.QShortcut(keyseq, ui.textedit)
        self.connect(shortcut, QtCore.SIGNAL('activated()'), self._choose_font)
        ui.hsplitter.splitterMoved.connect(self._splitter_update)
        ui.vsplitter.splitterMoved.connect(self._splitter_update)
        ui.fsplitter.splitterMoved.connect(self._splitter_update)
        
        self._formats = {}
        self._last_text_len = 0
        self._last_warnings = {}
        self._ui_change_timer = QtCore.QTimer()
        self._ui_change_timer.timeout.connect(self._timer_exhaust)
        
        # load last user settings
        self._load_preferences()

    def set_model(self, model):
        """assign the model that backs up the view"""
        self._model = model
        self._warnreportview.setModel(model.get_warnreport())
        self._ui.filetree.setModel(model.get_filetree())
        for col in xrange(1, model.get_filetree().columnCount()):
            self._ui.filetree.setColumnHidden(col, True)
        index = model.get_filetree().index(os.path.expanduser('~'))
        self._ui.filetree.setRootIndex(index)

    def set_focus_textedit(self):
        """set the focus back to the textedit to resume editing"""
        self._ui.textedit.activateWindow()
        self._ui.textedit.setFocus()

    @staticmethod
    def differentiate(old, new):
        """compute the differential between the previous set of warnings and
           the latest processed one, returning a dictionary of line-indexed
           warning levels"""
        sold = set(old)
        snew = set(new)
        mark, sweep = snew.difference(sold), sold.difference(snew)
        dwarn = {}
        for m in mark:
            dwarn[m] = new[m]
        for s in sweep:
            dwarn[s] = 0
        return dwarn
        
    def refresh(self):
        """called from a worker thread, need to dispath the event with the
           help of a slot/signal"""
        self._lock.acquire()
        self._docs.append(self._model.get_html())
        self._lock.release()
        self.emit(QtCore.SIGNAL('_reload()'))

    def select_line(self, line):
        textedit = self._ui.textedit
        cursor = textedit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start, 
                            QtGui.QTextCursor.MoveAnchor, 1)
        cursor.movePosition(QtGui.QTextCursor.Down, 
                            QtGui.QTextCursor.MoveAnchor, line-1)
        textedit.setTextCursor(cursor)
    
    def set_rest(self, rest):
        self._ui.textedit.setPlainText(QtCore.QString(rest))
        
    #-------------------------------------------------------------------------
    # Signal handlers (slots)
    #-------------------------------------------------------------------------

    def _textedit_update(self):
        """^: something in the textedit widget has been updated"""
        # Ok, so textChanged is stupid, as it gets signalled when *text*
        # is not changed but formatting is. So we need to discriminate from
        # both kind of calls...
        text = self._ui.textedit.toPlainText()
        if len(text) != self._last_text_len:
            self._last_text_len = len(text)
            self._model.update_rest(text)
    
    def _blockcount_update(self, newcount):
        """^: a new line has been added or an existing line got removed"""
        self._update_line()

    def _choose_font(self):
        """^: user requested the font dialog for the textedit window"""
        font = self._ui.textedit.font()
        (font, ok) = QtGui.QFontDialog.getFont(font)
        if ok:
            self._ui.textedit.setFont(font)
            self._save_preferences()

    def _splitter_update(self, pos, index):
        """^: a splitter has been moved"""
        self._ui_change_timer.stop()
        self._ui_change_timer.start(1000)
        
    def _select_file(self, index):
        path = self._ui.filetree.model().filePath(index)
        if os.path.isfile(path):
            self._model.replace(path)

    def _reload(self):
        """^: internal handler to refresh the textedit content asynchronously"""
        self._lock.acquire()
        doc = self._docs.pop(0)
        self._lock.release()
        self._ui.webview.setHtml(doc)
        self._warnreportview.refresh()
        self._update_background()

    def _timer_exhaust(self):
        """^: timer-filtered event handler for rapid changing UI mods"""
        self._save_preferences()


    #-------------------------------------------------------------------------
    # Private implementation
    #-------------------------------------------------------------------------
    
    def _update_background(self):
        """update the background color of all lines that contain errors"""
        lines = self._model.get_warnreport().get_lines()
        warnings = self.differentiate(self._last_warnings, lines) 
        self._last_warnings = lines
        for line in sorted(warnings):
            self._set_line_background(line, warnings[line])
    
    def _update_line(self):
        """update the background color of a single line
           it is usually called whenever a new line is inserted or removed, to
           avoid propagating colored background to a valid line
        """
        textedit = self._ui.textedit
        cursor = textedit.textCursor()
        line = cursor.blockNumber()
        lines = filter(lambda x: x>0, [line-1, line, line+1])
        for line in lines:
            level = line in self._last_warnings and \
                self._last_warnings[line] or 0
            self._set_line_background(line, level)

    def _set_line_background(self, line, level):
        """does the actual line background colorization"""
        textedit = self._ui.textedit
        if line > textedit.blockCount():
            # this may happen when the last error line is the last line in
            # the text edit widget
            return
        if not self._formats:
            self._generate_formats()
        line = line-1
        cursor = textedit.textCursor()
        cline = cursor.blockNumber()
        delta = line-cline
        if delta < 0:
            move = cursor.movePosition(QtGui.QTextCursor.Up, 
                                       QtGui.QTextCursor.MoveAnchor,
                                       abs(delta))
        elif delta > 0:
            move = cursor.movePosition(QtGui.QTextCursor.Down, 
                                       QtGui.QTextCursor.MoveAnchor,
                                       abs(delta))
        else:
            move = False
        cursor.setBlockFormat(self._formats[level])
        return move

    def _generate_formats(self):
        """generate background colors for textedit warnings"""
        if self._formats:
            return
        textedit = self._ui.textedit
        format = textedit.document().findBlock(0).blockFormat()
        self._formats[0] = format
        hues = (120, 60, 30, 0)
        for lvl, hue in enumerate(hues):
            format = QtGui.QTextBlockFormat(format)
            color = QtGui.QColor()
            color.setHsv(hue, 95, 255)
            format.setBackground(color)
            self._formats[lvl+1] = format.toBlockFormat()

    def _load_preferences(self):
        """reload previously saved UI configuration from a file"""
        # could use a QSetting object, but the API is just boring
        config = EasyConfigParser()
        if not config.read(os.path.expanduser('~/.ezsphinxrc')):
            return
        font = config.get('textedit', 'font')
        if font:
            qtfont = QtGui.QFont()
            if qtfont.fromString(font):
                self._ui.textedit.setFont(qtfont)
        for splitter in ('hsplitter', 'vsplitter', 'fsplitter'):
            sp = config.get('main', splitter)
            if sp:
                getattr(self._ui, splitter).restoreState(unhexlify(sp))

    def _save_preferences(self):
        """save current UI configuration into a configuration file"""
        # could use a QSetting object, but the API is just boring
        config = EasyConfigParser()
        font = self._ui.textedit.font().toString()
        config.set('textedit', 'font', font)

        for splitter in ('hsplitter', 'vsplitter', 'fsplitter'):
            data = hexlify(getattr(self._ui, splitter).saveState())
            config.set('main', splitter, data)
        
        with open(os.path.expanduser('~/.ezsphinxrc'), 'w') as out_:
            config.write(out_)
