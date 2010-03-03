# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created: Thu Mar  4 00:01:02 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(929, 668)
        self.mainwidget = QtGui.QWidget(MainWindow)
        self.mainwidget.setMouseTracking(True)
        self.mainwidget.setObjectName("mainwidget")
        self.vlayout = QtGui.QVBoxLayout(self.mainwidget)
        self.vlayout.setObjectName("vlayout")
        self.vsplitter = QtGui.QSplitter(self.mainwidget)
        self.vsplitter.setOrientation(QtCore.Qt.Vertical)
        self.vsplitter.setHandleWidth(7)
        self.vsplitter.setObjectName("vsplitter")
        self.editwidget = QtGui.QWidget(self.vsplitter)
        self.editwidget.setObjectName("editwidget")
        self.hlayout = QtGui.QVBoxLayout(self.editwidget)
        self.hlayout.setObjectName("hlayout")
        self.hsplitter = QtGui.QSplitter(self.editwidget)
        self.hsplitter.setOrientation(QtCore.Qt.Horizontal)
        self.hsplitter.setHandleWidth(7)
        self.hsplitter.setObjectName("hsplitter")
        self.textwidget = QtGui.QWidget(self.hsplitter)
        self.textwidget.setObjectName("textwidget")
        self.textlayout = QtGui.QHBoxLayout(self.textwidget)
        self.textlayout.setObjectName("textlayout")
        self.textedit = QtGui.QPlainTextEdit(self.textwidget)
        self.textedit.setObjectName("textedit")
        self.textlayout.addWidget(self.textedit)
        self.webwidget = QtGui.QWidget(self.hsplitter)
        self.webwidget.setObjectName("webwidget")
        self.weblayout = QtGui.QHBoxLayout(self.webwidget)
        self.weblayout.setObjectName("weblayout")
        self.webview = QtWebKit.QWebView(self.webwidget)
        self.webview.setUrl(QtCore.QUrl("about:blank"))
        self.webview.setObjectName("webview")
        self.weblayout.addWidget(self.webview)
        self.hlayout.addWidget(self.hsplitter)
        self.tablewidget = QtGui.QWidget(self.vsplitter)
        self.tablewidget.setObjectName("tablewidget")
        self.tablelayout = QtGui.QHBoxLayout(self.tablewidget)
        self.tablelayout.setObjectName("tablelayout")
        self.vlayout.addWidget(self.vsplitter)
        MainWindow.setCentralWidget(self.mainwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 929, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "ezSphinx", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
