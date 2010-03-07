#!/usr/bin/env python

from PyQt4.QtGui import QApplication
from controller import EzSphinxController
import sys


class EzSphinxApp(QApplication):
    """EzSphinx application"""
    
    def __init__(self, argv):
        QApplication.__init__(self, argv)
        self.aboutToQuit.connect(self._quit)

    def run(self):
        self._controller = EzSphinxController(self)
        self._controller.run()
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
