#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui
from view import ESphinxView, WarningReportView
from model import ESphinxModel

class EzSphinxApp(QtGui.QApplication):
    """
    """
    
    def __init__(self, argv):
        QtGui.QApplication.__init__(self, argv)
        self.connect(self, QtCore.SIGNAL('aboutToQuit()'), self._quit)

    def run(self):
        self._model = ESphinxModel()
        self._view = ESphinxView()
        self._model.add_view(self._view)
        self._view.show()
        return self.exec_()
        
    def _quit(self):
        self._model.quit()
        

def main():
    app = EzSphinxApp(sys.argv)
    sys.exit(app.run())
     
if __name__ == "__main__":
    app = EzSphinxApp(sys.argv)
    sys.exit(app.run())
