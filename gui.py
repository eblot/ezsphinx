# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created: Sat Feb 27 15:26:25 2010
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
        self.verticalLayout = QtGui.QVBoxLayout(self.mainwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.twsplitter = QtGui.QSplitter(self.mainwidget)
        self.twsplitter.setOrientation(QtCore.Qt.Horizontal)
        self.twsplitter.setHandleWidth(3)
        self.twsplitter.setObjectName("twsplitter")
        self.horizontalLayoutWidget = QtGui.QWidget(self.twsplitter)
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.textlayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.textlayout.setObjectName("textlayout")
        self.textedit = QtGui.QPlainTextEdit(self.horizontalLayoutWidget)
        self.textedit.setObjectName("textedit")
        self.textlayout.addWidget(self.textedit)
        self.horizontalLayoutWidget_2 = QtGui.QWidget(self.twsplitter)
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.weblayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.weblayout.setObjectName("weblayout")
        self.webview = QtWebKit.QWebView(self.horizontalLayoutWidget_2)
        self.webview.setUrl(QtCore.QUrl("about:blank"))
        self.webview.setObjectName("webview")
        self.weblayout.addWidget(self.webview)
        self.verticalLayout.addWidget(self.twsplitter)
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
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
