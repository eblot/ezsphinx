from PyQt4.QtCore import Qt, QUrl
from PyQt4.QtGui import QFrame, QKeySequence, QShortcut
from PyQt4.QtWebKit import QWebView


class EzSphinxWebView(QWebView):
    """Web view to render Restructed Text"""
    
    ZOOM_STEP = 0.1
    ZOOM_DEFAULT = 0.8
    
    def __init__(self, parent, mainwin):
        QWebView.__init__(self, parent)
        self.mainwin = mainwin
        self.setUrl(QUrl("about:blank"))
        self.setObjectName("webview")
        self.setTextSizeMultiplier(self.ZOOM_DEFAULT)
        shortcut = QShortcut(QKeySequence.ZoomIn, self)
        shortcut.activated.connect(self._zoom_in)
        shortcut.setContext(Qt.WidgetShortcut)
        shortcut = QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Equal), self)
        shortcut.activated.connect(self._zoom_neutral)
        shortcut.setContext(Qt.WidgetShortcut)
        shortcut = QShortcut(QKeySequence.ZoomOut, self)
        shortcut.activated.connect(self._zoom_out)
        shortcut.setContext(Qt.WidgetShortcut)
    
    def refresh(self, html):
        self.setHtml(html)

    def load_presentation(self, config):
        if 'web' in config:
            web = config['web']
            for key, value in web:
                if key == 'zoom':
                    zoom = float(value)
                    self.setTextSizeMultiplier(zoom)

    #-------------------------------------------------------------------------
    # Private implementation
    #-------------------------------------------------------------------------
    
    def _zoom_in(self):
        self.setTextSizeMultiplier(self.textSizeMultiplier()+self.ZOOM_STEP)
        self._save_preferences()

    def _zoom_neutral(self):
        self.setTextSizeMultiplier(self.ZOOM_DEFAULT)
        self._save_preferences()

    def _zoom_out(self):
        self.setTextSizeMultiplier(self.textSizeMultiplier()-self.ZOOM_STEP)
        self._save_preferences()

    def _save_preferences(self):
        """save current UI configuration into a configuration file"""
        config = {'web' : [('zoom', str(self.textSizeMultiplier()))]}
        self.mainwin.save_presentation(config)
