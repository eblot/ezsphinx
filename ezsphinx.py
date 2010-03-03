#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui
from view import ESphinxView, WarningReportView
from model import ESphinxModel
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    model = ESphinxModel()
    view = ESphinxView()
    model.add_view(view)
    view.show()
    sys.exit(app.exec_())
