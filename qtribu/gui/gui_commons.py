#! python3  # noqa: E265

"""
Common GUI utils.
"""

# PyQGIS
from qgis.PyQt.QtCore import QRegularExpression
from qgis.PyQt.QtGui import QRegularExpressionValidator

# -- VALIDATORS

# alphanumeric
_alphanum_qreg = QRegularExpression("[a-z-A-Z-0-9-_]+")
QVAL_ALPHANUM = QRegularExpressionValidator(_alphanum_qreg)

# alphanumeric extended
_alphanumx_qreg = QRegularExpression("[a-z-A-Z-0-9-_-.--]+")
QVAL_ALPHANUMX = QRegularExpressionValidator(_alphanumx_qreg)

# emails
_email_qreg = QRegularExpression(
    "\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,4}\\b",
    QRegularExpression.CaseInsensitiveOption,
)
QVAL_EMAIL = QRegularExpressionValidator(_email_qreg)

# URL
_url_qreg = QRegularExpression(
    r"^https?://(?:[-\w.\/]|(?:%[\da-fA-F]{2}))+",
    QRegularExpression.UseUnicodePropertiesOption,
)
QVAL_URL = QRegularExpressionValidator(_url_qreg)
