from PyQt4.QtCore import QFileSystemWatcher, QMetaObject, QObject, QRect, \
                         Qt, QTimer, QUrl, SIGNAL
from PyQt4.QtGui import QAbstractItemView, \
                        QColor, QFontDialog, QHBoxLayout, QKeySequence, \
                        QMainWindow, QMenuBar, QPlainTextEdit, QShortcut, \
                        QSplitter, QStatusBar, QTableView, QTextBlockFormat, \
                        QTextCursor, QTreeView, QVBoxLayout, QWidget
from PyQt4.QtWebKit import QWebView

from ConfigParser import SafeConfigParser as ConfigParser
from binascii import hexlify, unhexlify
import os
import tempfile
import time 
import threading

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


class EzSphinxMenuBar(QMenuBar):
    """Main menu bar"""
    
    def __init__(self, parent):
        QMenuBar.__init__(self, parent)
        # TBD: manage the size
        self.setGeometry(QRect(0, 0, 929, 22))
        self.setObjectName("menubar")
        self.setNativeMenuBar(True)
        # file_menu = self.addMenu(self.tr("&File"));

class EzSphinxStatusBar(QStatusBar):
    """Status bar of the main window"""

    def __init__(self, parent):
        QStatusBar.__init__(self, parent)
        self.setObjectName("statusbar")


class EzSphinxTextEdit(QPlainTextEdit):
    """Source window for Restructured Text"""
    
    def __init__(self, parent):
        QPlainTextEdit.__init__(self, parent)
        self.setObjectName("textedit")
        self._formats = {}
        self.textChanged.connect(self._textedit_update)
        self.blockCountChanged.connect(self._blockcount_update)
        
        self._last_warnings = 0 # should be moved into the document

    def select_line(self, line):
        """Move the edit cursor to the selected line"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor, 1)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line-1)
        self.setTextCursor(cursor)
    
    def set_focus(self):
        """set the focus back to the textedit to resume editing"""
        self.activateWindow()
        self.setFocus()

    def set_rest(self, rest):
        self.setPlainText(QtCore.QString(rest))

    def refresh(self):
        super(EzSphinxTextEdit, self).refresh()
        self._update_background()

    def load_presentation(self, config):
        font = config.get('textedit', 'font')
        if font:
            qtfont = QFont()
            if qtfont.fromString(font):
                self.setFont(qtfont)
        
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
           avoid propagating colored background to a valid line"""
        cursor = self.textCursor()
        line = cursor.blockNumber()
        lines = filter(lambda x: x>0, [line-1, line, line+1])
        for line in lines:
            level = line in self._last_warnings and \
                self._last_warnings[line] or 0
            self._set_line_background(line, level)

    def _set_line_background(self, line, level):
        """does the actual line background colorization"""
        if line > self.blockCount():
            # this may happen when the last error line is the last line in
            # the text edit widget
            return
        if not self._formats:
            self._generate_formats()
        line = line-1
        cursor = self.textCursor()
        cline = cursor.blockNumber()
        delta = line-cline
        if delta < 0:
            move = cursor.movePosition(QTextCursor.Up, QTextCursor.MoveAnchor,
                                       abs(delta))
        elif delta > 0:
            move = cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor,
                                       abs(delta))
        else:
            move = False
        cursor.setBlockFormat(self._formats[level])
        return move

    def _choose_font(self):
        """^: user requested the font dialog for the textedit window"""
        font = self.font()
        (font, ok) = QFontDialog.getFont(font)
        if ok:
            self.setFont(font)
            config = {'textedit' : [('font', font.toString())]}
            self.parent.save_presentation(config)

    def _generate_formats(self):
        """generate background colors for textedit warnings"""
        if self._formats:
            return
        format = self.document().findBlock(0).blockFormat()
        self._formats[0] = format
        hues = (120, 60, 30, 0)
        for lvl, hue in enumerate(hues):
            format = QTextBlockFormat(format)
            color = QColor()
            color.setHsv(hue, 95, 255)
            format.setBackground(color)
            self._formats[lvl+1] = format.toBlockFormat()


class EzSphinxWebView(QWebView):
    """Web view to render Restructed Text"""
    
    def __init__(self, parent):
        QWebView.__init__(self, parent)
        self.setUrl(QUrl("about:blank"))
        self.setObjectName("webview")
        self.setTextSizeMultiplier(0.8)


class WarningReportView(QTableView):
    """Report the warnings and errors within a table"""

    def __init__(self, view): 
        QTableView.__init__(self) 
        self._parentview = view
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        font = QFont()
        font.setWeight(QFont.Bold)
        self.setAlternatingRowColors(True)
        header = self.horizontalHeader()
        header.setFont(font) 
        header.setStretchLastSection(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def currentChanged(self, current, previous):
        row = current.row()
        line = self.model().get_line(row)
        self._parentview.select_warning(line)

    def refresh(self):
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeRowsToContents()


class EzSphinxTreeView(QTreeView):
    """File tree view"""
    
    def __init__(self, parent):
        QTreeView.__init__(self, parent)
        self.setObjectName("filetree")
        self.setSortingEnabled(True)
        self.setColumnWidth(0, 50)
        font = self.font()
        font.setPointSize(10)
        self.setFont(font)
        self.setHeaderHidden(True)
        filetree.clicked.connect(self._select_file)
    
    def _select_file(self, index):
        """^: invoked when a file or a directory is selected"""
        path = self.model().filePath(index)
        if os.path.isfile(path):
            self._model.replace(path)


class EzSphinxSplitter(QSplitter):
    """A splitter that backs up its presentation"""
    
    def __init__.(self, parent, name, orientation):
        QSplitter.__init__(self, parent)
        self.setOrientation(orientation)
        self.setHandleWidth(7)
        self.setObjectName(name)
        self.splitterMoved.connect(self._update_position)
        self._timer = QTimer()
        self._timer.timeout.connect(self._timer_exhaust)
 
    def load_presentation(self, config):
        if 'main' in config:
            main = config['main']
            for key, value in main:
                if key == self.objectName().toUtf8():
                    self.restoreState(unhexlify(value))
    
    #-------------------------------------------------------------------------
    # Signal handlers (slots)
    #-------------------------------------------------------------------------

    def _update_position(self, pos, index):
        """^: a splitter has been moved"""
        self._timer.stop()
        self._timer.start(1000)

    def _timer_exhaust(self):
        """^: timer-filtered event handler for rapid changing UI mods"""
        data = hexlify(splitter.saveState())
        config = {'main' : [(str(splitter.objectName().toUtf8()), data)]}
        self.parent.save_presentation(config)


class EzSphinxWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        QMainWindow.__init__(self)
        self.setObjectName("EzSphinx")
        self.resize(929, 668)
        self.setWindowTitle("EzSphinx")
        QMetaObject.connectSlotsByName(self)
        self.config = EasyConfigParser()
        self._setup_ui()
        
        keyseq = QKeySequence("Ctrl+T")
        shortcut = QShortcut(keyseq, ui.textedit)
        self.connect(shortcut, SIGNAL('activated()'), self._choose_font)
    
    def save_presentation(self, config):
        self._save_preferences(config)
    
    #-------------------------------------------------------------------------
    # Private implementation
    #-------------------------------------------------------------------------

    def _setup_ui(self):
        mainwidget = QWidget(self)
        mainwidget.setMouseTracking(True)
        mainwidget.setObjectName("mainwidget")
        flayout = QHBoxLayout(mainwidget)
        flayout.setObjectName("flayout")
        fsplitter = EzSphinxSplitter(mainwidget, 'fsplitter', Qt.Horizontal)
        ftwidget = QWidget(fsplitter)
        ftwidget.setObjectName("ftwidget")
        ftlayout = QVBoxLayout(ftwidget)
        ftlayout.setObjectName("ftlayout")
        ftlayout.setContentsMargins(0,4,1,0)
        self.filetree = EzSphinxTreeView(ftwidget)
        ftlayout.addWidget(filetree)
        vlayout = QVBoxLayout(fsplitter)
        vlayout.setObjectName("vlayout")
        vlayout.setContentsMargins(4,0,4,0)
        vsplitter = EzSphinxSplitter(fsplitter, 'vsplitter', Qt.Vertical)
        editwidget = QWidget(vsplitter)
        editwidget.setObjectName("editwidget")
        elayout = QVBoxLayout(editwidget)
        elayout.setObjectName("elayout")
        elayout.setContentsMargins(1,4,1,0)
        hsplitter = EzSphinxSplitter(editwidget, 'hsplitter', Qt.Horizontal)
        elayout.addWidget(hsplitter)
        textwidget = QWidget(hsplitter)
        textwidget.setObjectName("textwidget")
        textlayout = QHBoxLayout(textwidget)
        textlayout.setObjectName("textlayout")
        textlayout.setContentsMargins(0,0,2,0)
        self.textedit = EzSphinxTextEdit(textwidget)
        textlayout.addWidget(self.textedit)
        webwidget = QWidget(hsplitter)
        webwidget.setObjectName("webwidget")
        weblayout = QHBoxLayout(webwidget)
        weblayout.setObjectName("weblayout")
        weblayout.setContentsMargins(1,0,2,2)
        self.webview = EzSphinxWebView(webwidget)
        weblayout.addWidget(self.webview)
        tablewidget = QWidget(vsplitter)
        tablewidget.setObjectName("tablewidget")
        tablelayout = QHBoxLayout(tablewidget)
        tablelayout.setObjectName("tablelayout")
        tablelayout.setContentsMargins(1,0,2,0)
        vlayout.addWidget(vsplitter)
        flayout.addWidget(fsplitter)
        self.warnreport = WarningReportView(self)
        tablelayout.addWidget(self.warnreport)
        self.setCentralWidget(mainwidget)
        self.setMenuBar(EzSphinxMenuBar(self))
        self.setStatusBar(EzSphinxStatusBar(self))
        
    def _load_preferences(self):
        """reload previously saved UI configuration from a file"""
        if not self.config.read(os.path.expanduser('~/.ezsphinxrc')):
            return

    def _save_preferences(self, config={}):
        """save current UI configuration into a configuration file"""
        for section in config:
            for key, value in section:
                config.set(section, key, value)

        with open(os.path.expanduser('~/.ezsphinxrc'), 'w') as out_:
            self.config.write(out_)


class ESphinxView(QWidget):
    """
    """
    
    def show(self):
        self._ui.show()
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._model = None
        ui = EzSphinxWindow()
        self._ui = ui
        # ui.setupUi(self)
        #self.watcher = QtCore.QFileSystemWatcher(self)
        #QtCore.QObject.connect(self.ui.button_open,QtCore.SIGNAL("clicked()"), self.file_dialog)
        #QtCore.QObject.connect(self.ui.button_save,QtCore.SIGNAL("clicked()"), self.file_save)
        #QtCore.QObject.connect(self.ui.editor_window,QtCore.SIGNAL("textChanged()"), self.enable_save)
        #QtCore.QObject.connect(self.watcher,QtCore.SIGNAL("fileChanged(const QString&)"), self.file_changed)
        #self.filename = False
        QObject.connect(self, SIGNAL("_reload()"), self._reload)
        self._lock = threading.Lock()
        self._docs = []

        self._formats = {}
        self._last_text_len = 0
        self._last_warnings = {}
        
        # load last user settings
        self._load_preferences()

    def set_model(self, model):
        """assign the model that backs up the view"""
        self._model = model
        self._ui._warnreport.setModel(model.get_warnreport())
        self._ui.filetree.setModel(model.get_filetree())
        for col in xrange(1, model.get_filetree().columnCount()):
            self._ui.filetree.setColumnHidden(col, True)
        index = model.get_filetree().index(os.path.expanduser('~'))
        self._ui.filetree.setRootIndex(index)

    def refresh(self):
        """called from a worker thread, need to dispath the event with the
           help of a slot/signal"""
        self._lock.acquire()
        self._docs.append(self._model.get_html())
        self._lock.release()
        self.emit(SIGNAL('_reload()'))

    def set_rest(self, rest):
        print "Should be called from document"
        self.textedit.setPlainText(QtCore.QString(rest))
    
    def select_warning(self, line):
        self.textedit.select_line(line)
        self.textedit.set_focus()
        
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

    def _reload(self):
        """^: internal handler to refresh the textedit content asynchronously"""
        self._lock.acquire()
        doc = self._docs.pop(0)
        self._lock.release()
        self._ui.webview.setHtml(doc)
        self.warnreport.refresh()
        self.textedit.refresh()
