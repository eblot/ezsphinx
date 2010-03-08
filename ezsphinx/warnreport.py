from PyQt4.QtCore import QAbstractTableModel, Qt, QVariant
from PyQt4.QtGui import QAbstractItemView, QApplication, QFont, QTableView


class EzSphinxWarnReportView(QTableView):
    """Report the warnings and errors within a table"""

    def __init__(self, view): 
        QTableView.__init__(self) 
        self._parentview = view
        self.setObjectName("warnreport")
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
        self.setModel(QApplication.instance().warnreport)

    def currentChanged(self, current, previous):
        row = current.row()
        line = self.model().get_line(row)
        self._parentview.select_warning(line)

    def refresh(self):
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeRowsToContents()


class EzSphinxWarnReportModel(QAbstractTableModel):
    """Track the warnings within a ReST document"""
    
    columns = ('Line', 'Level', 'Description')
    levels = ('Debug', 'Info', 'Warning', 'Error', 'Severe')
    
    def __init__(self, parent=None): 
        QAbstractTableModel.__init__(self, parent)
        self._warnings = []
    
    def rowCount(self, parent=None):
        return len(self._warnings)
    
    def columnCount(self, parent=None):
        return len(self.columns)
    
    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()
        item = self._warnings[index.row()][index.column()]
        if index.column() == 1:
            item = self.levels[item]
        return QVariant(item)
    
    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation != Qt.Horizontal:
            return QVariant(int(section)+1)
        return QVariant(self.columns[section])
        
    def reset(self):
        QAbstractTableModel.reset(self)
        self._warnings = []
    
    def add(self, level=0, line=0, desc=''):
        self._warnings.append((line, level, desc))
        self.insertRows(0, 1)
    
    def get_line(self, row):
        try:
            return self._warnings[row][0]
        except KeyError:
            return 0
    
    def get_lines(self):
        lines = {}
        for w in self._warnings:
            lines[w[0]] = w[1]
        return lines
