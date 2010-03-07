from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QSplitter
from binascii import hexlify, unhexlify

class EzSphinxSplitter(QSplitter):
    """A splitter that backs up its presentation"""
    
    def __init__(self, parent, mainwin, name, orientation):
        QSplitter.__init__(self, parent)
        self.mainwin = mainwin
        self.setOrientation(orientation)
        self.setHandleWidth(7)
        self.setObjectName(name)
        self.splitterMoved.connect(self._update_position)
        self._timer = QTimer()
        self._timer.timeout.connect(self._timer_exhaust)
 
    def load_presentation(self, config):
        if 'main' in config:
            main = config['main']
            for key, value in main:
                if key == self.objectName().toUtf8():
                    self.restoreState(unhexlify(value))
    
    #-------------------------------------------------------------------------
    # Signal handlers (slots)
    #-------------------------------------------------------------------------

    def _update_position(self, pos, index):
        """^: a splitter has been moved"""
        self._timer.stop()
        self._timer.start(1000)

    def _timer_exhaust(self):
        """^: timer-filtered event handler for rapid changing UI mods"""
        data = hexlify(self.saveState())
        config = {'main' : [(str(self.objectName().toUtf8()), data)]}
        self.mainwin.save_presentation(config)
