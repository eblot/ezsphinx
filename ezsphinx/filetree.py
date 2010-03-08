from PyQt4.QtCore import QDir
from PyQt4.QtGui import QApplication, QDirModel, QTreeView
import os


class EzSphinxTreeView(QTreeView):
    """File tree view"""
    
    def __init__(self, parent):
        QTreeView.__init__(self, parent)
        self.setObjectName("filetree")
        self.setSortingEnabled(True)
        self.setColumnWidth(0, 50)
        font = self.font()
        font.setPointSize(10)
        self.setFont(font)
        self.setHeaderHidden(True)
        self.setModel(QApplication.instance().filetree)
        for col in xrange(1, self.model().columnCount()):
            self.setColumnHidden(col, True)
        self.setRootIndex(self.model().index(os.path.expanduser('~')))
        self.clicked.connect(self._select_file)
    
    def _select_file(self, index):
        """^: invoked when a file or a directory is selected"""
        path = self.model().filePath(index)
        if os.path.isfile(path):
            QApplication.instance().controller().load_file(path)


class EzSphinxFileTreeModel(QDirModel):
    """File tree browser"""

    def __init__(self):
        QDirModel.__init__(self)
        self.setFilter(QDir.Dirs | QDir.NoDotAndDotDot | QDir.Files)
