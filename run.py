#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui
from view import ESphinxGui
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    gui = ESphinxGui()
    gui.show()
    sys.exit(app.exec_())
