import re

from qgis.PyQt.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetricsF,
    QPalette,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextLayout,
)


class MarkdownHighlighter(QSyntaxHighlighter):

    MARKDOWN_KEYS_REGEX = {
        "Bold": re.compile("(?P<delim>\*\*)(?P<text>.+)(?P=delim)"),
        "uBold": re.compile("(?P<delim>__)(?P<text>[^_]{2,})(?P=delim)"),
        "Italic": re.compile("(?P<delim>\*)(?P<text>[^*]{2,})(?P=delim)"),
        "uItalic": re.compile("(?P<delim>_)(?P<text>[^_]+)(?P=delim)"),
        "Link": re.compile("(?u)(^|(?P<pre>[^!]))\[.*?\]:?[ \t]*\(?[^)]+\)?"),
        "Image": re.compile("(?u)!\[.*?\]\(.+?\)"),
        "HeaderAtx": re.compile("(?u)^\#{1,6}(.*?)\#*(\n|$)"),
        "Header": re.compile("^(.+)[ \t]*\n(=+|-+)[ \t]*\n+"),
        "CodeBlock": re.compile("^([ ]{4,}|\t).*"),
        "UnorderedList": re.compile("(?u)^\s*(\* |\+ |- )+\s*"),
        "UnorderedListStar": re.compile("^\s*(\* )+\s*"),
        "OrderedList": re.compile("(?u)^\s*(\d+\. )\s*"),
        "BlockQuote": re.compile("(?u)^\s*>+\s*"),
        "BlockQuoteCount": re.compile("^[ \t]*>[ \t]?"),
        "CodeSpan": re.compile("(?P<delim>`+).+?(?P=delim)"),
        "HR": re.compile("(?u)^(\s*(\*|-)\s*){3,}$"),
        "eHR": re.compile("(?u)^(\s*(\*|=)\s*){3,}$"),
        "Html": re.compile("<.+?>"),
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        parent.setTabStopDistance(
            QFontMetricsF(parent.font()).horizontalAdvance(" ") * 4
        )

        self.defaultTheme = {
            "background-color": "#d7d7d7",
            "color": "#191970",
            "bold": {"color": "#859900", "font-weight": "bold", "font-style": "normal"},
            "emphasis": {
                "color": "#b58900",
                "font-weight": "bold",
                "font-style": "italic",
            },
            "link": {
                "color": "#cb4b16",
                "font-weight": "normal",
                "font-style": "normal",
            },
            "image": {
                "color": "#cb4b16",
                "font-weight": "normal",
                "font-style": "normal",
            },
            "header": {
                "color": "#2aa198",
                "font-weight": "bold",
                "font-style": "normal",
            },
            "unorderedlist": {
                "color": "#dc322f",
                "font-weight": "normal",
                "font-style": "normal",
            },
            "orderedlist": {
                "color": "#dc322f",
                "font-weight": "normal",
                "font-style": "normal",
            },
            "blockquote": {
                "color": "#dc322f",
                "font-weight": "normal",
                "font-style": "normal",
            },
            "codespan": {
                "color": "#dc322f",
                "font-weight": "normal",
                "font-style": "normal",
            },
            "codeblock": {
                "color": "#ff9900",
                "font-weight": "normal",
                "font-style": "normal",
            },
            "line": {
                "color": "#2aa198",
                "font-weight": "normal",
                "font-style": "normal",
            },
            "html": {
                "color": "#c000c0",
                "font-weight": "normal",
                "font-style": "normal",
            },
        }
        self.setTheme(self.defaultTheme)

    def setTheme(self, theme):
        self.theme = theme
        self.MARKDOWN_KWS_FORMAT = {}

        pal = self.parent.palette()
        pal.setColor(QPalette.Base, QColor(theme["background-color"]))
        self.parent.setPalette(pal)
        self.parent.setTextColor(QColor(theme["color"]))

        text_char_format = QTextCharFormat()
        text_char_format.setForeground(QBrush(QColor(theme["header"]["color"])))
        text_char_format.setFontWeight(
            QFont.Bold if theme["header"]["font-weight"] == "bold" else QFont.Normal
        )
        text_char_format.setFontItalic(
            True if theme["header"]["font-style"] == "italic" else False
        )
        self.MARKDOWN_KWS_FORMAT["HeaderAtx"] = text_char_format

        self.rehighlight()

    def highlightBlock(self, text):
        text = str(text)
        self.highlightMarkdown(text, 0)

    def highlightMarkdown(self, text, strt):
        cursor = QTextCursor(self.document())
        bf = cursor.blockFormat()
        self.setFormat(0, len(text), QColor(self.theme["color"]))

        if self.highlightAtxHeader(text, cursor, bf, strt):
            return

    def highlightEmptyLine(self, text, cursor, bf, strt):
        textAscii = str(text.replace("\u2029", "\n"))
        if textAscii.strip():
            return False
        else:
            return True

    def highlightAtxHeader(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX["HeaderAtx"], text):
            # bf.setBackground(QBrush(QColor(7,54,65)))
            # cursor.movePosition(QTextCursor.End)
            # cursor.mergeBlockFormat(bf)
            self.setFormat(
                mo.start() + strt,
                mo.end() - mo.start(),
                self.MARKDOWN_KWS_FORMAT["HeaderAtx"],
            )
            found = True
        return found
