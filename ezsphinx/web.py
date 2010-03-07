class EzSphinxWebView(QWebView):
    """Web view to render Restructed Text"""
    
    def __init__(self, parent):
        QWebView.__init__(self, parent)
        self.setUrl(QUrl("about:blank"))
        self.setObjectName("webview")
        self.setTextSizeMultiplier(0.8)
    
    def refresh(self, html):
        self.setHtml(html)


