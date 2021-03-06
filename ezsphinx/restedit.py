from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QColor, QFileDialog, QFont, \
                        QFontDialog, QKeySequence, QPlainTextEdit, QShortcut, \
                        QTextBlockFormat, QTextCursor
import codecs


class EzSphinxRestEdit(QPlainTextEdit):
    """Source window for Restructured Text"""
    
    def __init__(self, parent, mainwin):
        QPlainTextEdit.__init__(self, parent)
        self.mainwin = mainwin
        self.setObjectName("restedit")
        self._formats = {}
        self.textChanged.connect(self._restedit_update)
        self.blockCountChanged.connect(self._blockcount_update)
        shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        shortcut.activated.connect(self._choose_font)
        shortcut = QShortcut(QKeySequence.ZoomIn, self)
        shortcut.activated.connect(self._zoom_in)
        shortcut.setContext(Qt.WidgetShortcut)
        shortcut = QShortcut(QKeySequence.ZoomOut, self)
        shortcut.activated.connect(self._zoom_out)
        shortcut.setContext(Qt.WidgetShortcut)
        self._doc = QApplication.instance().rest
        self._last_warnings = {} # should be moved to the document

    def select_line(self, line):
        """Move the edit cursor to the selected line"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor, 1)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line-1)
        self.setTextCursor(cursor)
    
    def set_focus(self):
        """set the focus back to the restedit to resume editing"""
        self.activateWindow()
        self.setFocus()

    def set_rest(self, rest):
        self.setPlainText(QtCore.QString(rest))

    def refresh(self):
        self._update_background()
    
    def update_text(self):
        self.setPlainText(self._doc.text)

    def load_presentation(self, config):
        if 'restedit' in config:
            for key, value in config['restedit']:
                if key == 'font':
                    qtfont = QFont()
                    if qtfont.fromString(value):
                        self.setFont(qtfont)
        
    @staticmethod
    def differentiate(old, new):
        """compute the differential between the previous set of warnings and
           the latest processed one, returning a dictionary of line-indexed
           warning levels"""
        sold = set(old)
        snew = set(new)
        mark, sweep = snew.difference(sold), sold.difference(snew)
        dwarn = {}
        for m in mark:
            dwarn[m] = new[m]
        for s in sweep:
            dwarn[s] = 0
        return dwarn

    #-------------------------------------------------------------------------
    # Signal handlers (slots)
    #-------------------------------------------------------------------------

    def _restedit_update(self):
        """^: something in the restedit widget has been updated"""
        self._doc.text = self.toPlainText()
    
    def _blockcount_update(self, newcount):
        """^: a new line has been added or an existing line got removed"""
        self._update_line()

    #-------------------------------------------------------------------------
    # Private implementation
    #-------------------------------------------------------------------------

    def _zoom_in(self):
        font = self.font()
        pointsize = font.pointSize()
        if pointsize < 25:
            pointsize += 1
            font.setPointSize(pointsize)
            self.setFont(font)
            self._save_preferences()

    def _zoom_out(self):
        font = self.font()
        pointsize = font.pointSize()
        if pointsize > 5:
            pointsize -= 1
            font.setPointSize(pointsize)
            self.setFont(font)
            self._save_preferences()

    def _update_background(self):
        """update the background color of all lines that contain errors"""
        lines = QApplication.instance().warnreport.get_lines()
        warnings = self.differentiate(self._last_warnings, lines) 
        self._last_warnings = lines
        for line in sorted(warnings):
            self._set_line_background(line, warnings[line])
    
    def _update_line(self):
        """update the background color of a single line
           it is usually called whenever a new line is inserted or removed, to
           avoid propagating colored background to a valid line"""
        cursor = self.textCursor()
        line = cursor.blockNumber()
        lines = filter(lambda x: x>0, [line-1, line, line+1])
        for line in lines:
            level = line in self._last_warnings and \
                self._last_warnings[line] or 0
            self._set_line_background(line, level)

    def _set_line_background(self, line, level):
        """does the actual line background colorization"""
        if line > self.blockCount():
            # this may happen when the last error line is the last line in
            # the text edit widget
            return
        if not self._formats:
            self._generate_formats()
        line = line-1
        cursor = self.textCursor()
        cline = cursor.blockNumber()
        delta = line-cline
        if delta < 0:
            move = cursor.movePosition(QTextCursor.Up, QTextCursor.MoveAnchor,
                                       abs(delta))
        elif delta > 0:
            move = cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor,
                                       abs(delta))
        else:
            move = False
        cursor.setBlockFormat(self._formats[level])
        return move

    def _choose_font(self):
        """^: user requested the font dialog for the restedit window"""
        font = self.font()
        (font, ok) = QFontDialog.getFont(font)
        if ok:
            self.setFont(font)
            self._save_preferences()
    
    def _save_preferences(self):
        config = {'restedit' : [('font', self.font().toString())]}
        self.mainwin.save_presentation(config)

    def _generate_formats(self):
        """generate background colors for restedit warnings"""
        if self._formats:
            return
        format = self.document().findBlock(0).blockFormat()
        self._formats[0] = format
        hues = (120, 60, 30, 0)
        for lvl, hue in enumerate(hues):
            format = QTextBlockFormat(format)
            color = QColor()
            color.setHsv(hue, 95, 255)
            format.setBackground(color)
            self._formats[lvl+1] = format.toBlockFormat()


class EzSphinxRestModel(object):
    """Restructured text document"""
    
    def __init__(self, **kw):
        self._text = ''
        self._dirty = False
        self._filepath = ''
        self._last_len = 0
        self._controller = QApplication.instance().controller()
    
    @property
    def dirty(self):
        return self._dirty
    
    @property
    def filename(self):
        return self._filepath

    def validate(self):
        """ Prompt the user if there are warnings/errors with reST file.
        """
        if len(self._warnings):
            return (False, "The reStructured Text is improperly composed." \
                           "Are you sure you want to save it?")
        else:
            return (True, '')

    def load(self, filename):
        """Load reST from a file"""
        fh = codecs.open(filename, 'r', 'utf-8')
        self._last_len = -1 # be sure to force a reload
        self.text = fh.read()
        fh.close()
        self._filepath = filename
        self._dirty = False
        return True

    def save(self, filename=None):
        """ Save reST to a file"""
        if filename:
            self._filepath = filename
        if not self._filepath:
            path = QFileDialog.getSaveFileName(filter='ReST (*.rst)')
            if not path:
                return False
            self._filepath = path
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
            self._controller.set_rest(text)

    text = property(_gettext, _settext)

