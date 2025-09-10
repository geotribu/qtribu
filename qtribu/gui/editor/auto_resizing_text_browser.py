"""A text editor that automatically adjusts its height to the height of the text
in its document when managed by a layout."""

# PyQGIS
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import QTextBrowser


class AutoResizingTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.textChanged.connect(self.updateGeometry)

    def hasHeightForWidth(self) -> bool:
        """Returns true if the widget's preferred height depends on its width; otherwise returns false.

        :return: hasHeightForWidth
        :rtype: bool
        """
        return True

    def heightForWidth(self, width: int) -> int:
        """Returns the preferred height for this widget, given the width w.

        If this widget has a layout, the default implementation returns the layout's preferred height. if there is no layout, the default implementation returns -1 indicating that the preferred height does not depend on the width.

        :param width: input width
        :type width: int
        :return: output height
        :rtype: int
        """
        margins = self.contentsMargins()

        if width >= margins.left() + margins.right():
            document_width = width - margins.left() - margins.right()
        else:
            # If specified width can't even fit the margin, there's no space left for the document
            document_width = 0

        # Cloning the whole document only to check its size at different width seems wasteful
        # but apparently it's the only and preferred way to do this in Qt >= 4. QTextDocument does not
        # provide any means to get height for specified width (as some QWidget subclasses do).
        # Neither does QTextEdit. In Qt3 Q3TextEdit had working implementation of heightForWidth()
        # but it was allegedly just a hack and was removed.
        #
        # The performance probably won't be a problem here because the application is meant to
        # work with a lot of small notes rather than few big ones. And there's usually only one
        # editor that needs to be dynamically resized - the one having focus.
        document = self.document().clone()
        document.setTextWidth(document_width)

        val = int(margins.top() + document.size().height() + margins.bottom())

        return val

    def sizeHint(self) -> QSize:
        """Recommended size for the widget

        :return: Recommended size
        :rtype: QSize
        """
        original_hint = super().sizeHint()
        return QSize(original_hint.width(), self.heightForWidth(original_hint.width()))
