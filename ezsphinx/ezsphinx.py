#!/usr/bin/env python

from PyQt4.QtGui import QApplication
from controller import EzSphinxController
from textedit import EzSphinxRestModel
from warnreport import EzSphinxWarnReportModel
from filetree import EzSphinxFileTreeModel
from main import EzSphinxWindow
import os
import sys


class EzSphinxApp(QApplication):
    """EzSphinx application"""
    
    def __init__(self, argv):
        QApplication.__init__(self, argv)
        self.aboutToQuit.connect(self._quit)

    @property
    def warnreport(self):
        return self._warnreport
    
    @property
    def filetree(self):
        return self._filetree

    @property
    def mainwin(self):
        return self._window

    @property
    def rest(self):
        return self._rest
    
    def run(self):
        self.setOrganizationName('MoaningMarmot')
        self.setOrganizationDomain('moaningmarmot.info')
        self.setApplicationName('EzSphinAx')
        self._controller = EzSphinxController(self)
        self._rest = EzSphinxRestModel()
        self._warnreport = EzSphinxWarnReportModel()
        self._filetree = EzSphinxFileTreeModel()
        self._window = EzSphinxWindow()
        self._window.show()
        return self.exec_()
    
    def controller(self):
        return self._controller
        
    def _quit(self):
        self._controller.quit()


def main():
    app = EzSphinxApp(sys.argv)
    sys.exit(app.run())
     
if __name__ == "__main__":
    app = EzSphinxApp(sys.argv)
    sys.exit(app.run())
