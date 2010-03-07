from PyQt4.QtCore import QAbstractTableModel, QDir, Qt, QVariant
from PyQt4.QtGui import QApplication, QDirModel, QFileDialog
import codecs
import os
import util


class WarningReportModel(QAbstractTableModel):
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


class FileTreeModel(QDirModel):
    """File tree browser"""

    def __init__(self):
        QDirModel.__init__(self)
        self.setFilter(QDir.Dirs | QDir.NoDotAndDotDot | QDir.Files)


class EzSphinxRestModel(object):
    """Restructured text document"""
    
    def __init__(self, **kw):
        self._text = ''
        self._dirty = False
        self._filepath = ''
        self._last_len = 0
        self._controller = QApplication.instance().controller()

    def validate(self):
        """ Prompt the user if there are warnings/errors with reST file.
        """
        if len(self._warnings):
            return (False, "The reStructured Text is improperly composed." \
                           "Are you sure you want to save it?")
        else:
            return (True, '')

    def replace(self, filename):
        if self._dirty:
            if not self.save():
                print "Not saved, cancelling load"
        return self.load(filename)
            
    def load(self, filename):
        """Load reST from a file"""
        fh = codecs.open(filename, 'r', 'utf-8')
        self._last_len = -1 # be sure to force a reload
        self.text = fh.read()
        fh.close()
        self._filepath = filename
        self._dirty = False
        return True

    def save(self):
        """ Save reST to a file"""
        print "SAVE?"
        if not self._filepath:
            path = QFileDialog.getSaveFileName(filter='ReST (*.rst)')
            if not path:
                return False
            self._filepath = path
        print "Save as %s" % unicode(self._filepath)
        fh = codecs.open(self._filepath, 'w', 'utf-8')
        fh.write(self.text)
        fh.close()
        self._dirty = False
        return True
    
    def _gettext(self):
        return self._text
        
    def _settext(self, text):
        # Ok, so textChanged is stupid, as it gets signalled when *text*
        # is not changed but formatting is. So we need to discriminate from
        # both kind of calls...
        self._text = text
        if len(text) != self._last_len:
            self._dirty = True
            self._last_len = len(text)
            # tell the controller the text has been updated
            self._controller.update_rest(text)

    text = property(_gettext, _settext)

