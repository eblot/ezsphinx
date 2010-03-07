from PyQt4.QtCore import QFileSystemWatcher, QMetaObject, QObject, QRect, \
                         Qt, QTimer, QUrl, SIGNAL
from PyQt4.QtGui import QAbstractItemView, QApplication, QColor, \
                        QFont, QFontDialog, QHBoxLayout, QKeySequence, \
                        QMainWindow, QMenuBar, QPlainTextEdit, QShortcut, \
                        QSplitter, QStatusBar, QTableView, QTextBlockFormat, \
                        QTextCursor, QTreeView, QVBoxLayout, QWidget
from PyQt4.QtWebKit import QWebView
from binascii import hexlify, unhexlify
from util import EasyConfigParser
import os
import time 


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
        # load last user settings
        self._load_preferences()
    
    def save_presentation(self, config):
        self._save_preferences(config)
    
    def select_warning(self, line):
        self.widgets['textedit'].select_line(line)
        self.widgets['textedit'].set_focus()

    def render(self, html=''):
        self.widgets['webview'].refresh(html) # a document would be better
        self.widgets['warnreport'].refresh()
        self.widgets['textedit'].refresh()
    
    def update_rest(self):
        self.widgets['textedit'].update_text()

    #-------------------------------------------------------------------------
    # Private implementation
    #-------------------------------------------------------------------------

    def _setup_ui(self):
        self.widgets = {}
        mainwidget = QWidget(self)
        mainwidget.setMouseTracking(True)
        mainwidget.setObjectName("mainwidget")
        flayout = QHBoxLayout(mainwidget)
        flayout.setObjectName("flayout")
        fsplitter = EzSphinxSplitter(mainwidget, self, 'fsplitter', 
                                     Qt.Horizontal)
        ftwidget = QWidget(fsplitter)
        ftwidget.setObjectName("ftwidget")
        ftlayout = QVBoxLayout(ftwidget)
        ftlayout.setObjectName("ftlayout")
        ftlayout.setContentsMargins(0,4,1,0)
        filetree = EzSphinxTreeView(ftwidget)
        ftlayout.addWidget(filetree)
        vlayout = QVBoxLayout(fsplitter)
        vlayout.setObjectName("vlayout")
        vlayout.setContentsMargins(4,0,4,0)
        vsplitter = EzSphinxSplitter(fsplitter, self, 'vsplitter', 
                                     Qt.Vertical)
        editwidget = QWidget(vsplitter)
        editwidget.setObjectName("editwidget")
        elayout = QVBoxLayout(editwidget)
        elayout.setObjectName("elayout")
        elayout.setContentsMargins(1,4,1,0)
        hsplitter = EzSphinxSplitter(editwidget, self, 'hsplitter', 
                                     Qt.Horizontal)
        elayout.addWidget(hsplitter)
        textwidget = QWidget(hsplitter)
        textwidget.setObjectName("textwidget")
        textlayout = QHBoxLayout(textwidget)
        textlayout.setObjectName("textlayout")
        textlayout.setContentsMargins(0,0,2,0)
        textedit = EzSphinxTextEdit(textwidget, self)
        textlayout.addWidget(textedit)
        webwidget = QWidget(hsplitter)
        webwidget.setObjectName("webwidget")
        weblayout = QHBoxLayout(webwidget)
        weblayout.setObjectName("weblayout")
        weblayout.setContentsMargins(1,0,2,2)
        webview = EzSphinxWebView(webwidget)
        weblayout.addWidget(webview)
        tablewidget = QWidget(vsplitter)
        tablewidget.setObjectName("tablewidget")
        tablelayout = QHBoxLayout(tablewidget)
        tablelayout.setObjectName("tablelayout")
        tablelayout.setContentsMargins(1,0,2,0)
        vlayout.addWidget(vsplitter)
        flayout.addWidget(fsplitter)
        warnreport = WarningReportView(self)
        tablelayout.addWidget(warnreport)
        self.setCentralWidget(mainwidget)
        self.setMenuBar(EzSphinxMenuBar(self))
        self.setStatusBar(EzSphinxStatusBar(self))
        self._add_widgets((hsplitter, vsplitter, fsplitter))
        self._add_widgets((filetree, textedit, webview, warnreport))

    def _add_widgets(self, widgets):
        if not isinstance(widgets, tuple) and not isinstance(widgets, list):
            widgets = (widgets,)
        for widget in widgets:
            name = str(widget.objectName().toUtf8())
            self.widgets[name] = widget
        
    def _load_preferences(self):
        """reload previously saved UI configuration from a file"""
        if not self.config.read(os.path.expanduser('~/.ezsphinxrc')):
            return
        config = {}
        for section in self.config.sections():
            for k, v in self.config.items(section):
                config.setdefault(section, []).append((k.lower(), v)) 
        for widget in self.widgets.values():
            if hasattr(widget, 'load_presentation'):
                widget.load_presentation(config)

    def _save_preferences(self, config={}):
        """save current UI configuration into a configuration file"""
        for section in config:
            for key, value in config[section]:
                self.config.set(section, key, value)

        with open(os.path.expanduser('~/.ezsphinxrc'), 'w') as out_:
            self.config.write(out_)
