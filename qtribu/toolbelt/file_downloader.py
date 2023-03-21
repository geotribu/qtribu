#! python3  # noqa: E265

"""
    Download remote files.
"""

# Standard library

# PyQGIS
from qgis.core import QgsFileDownloader
from qgis.PyQt.QtCore import QEventLoop, QUrl

# project
from qtribu.toolbelt.log_handler import PlgLogger

# ############################################################################
# ########## Globals ###############
# ##################################

plg_logger = PlgLogger()

# ############################################################################
# ########## Functions #############
# ##################################


def get_from_http(uri: str, output_path: str) -> str:
    """Download a file from a remote web server accessible through HTTP.

    :param uri: web URL to the file to download
    :type uri: str
    :param output_path: path to the local file
    :type output_path: str

    :return: output path
    :rtype: str
    """
    plg_logger.log(f"Downloading file from {uri} to {output_path}")

    # download it
    loop = QEventLoop()
    project_download = QgsFileDownloader(
        url=QUrl(uri), outputFileName=output_path, delayStart=True
    )
    project_download.downloadExited.connect(loop.quit)
    project_download.startDownload()
    loop.exec_()

    plg_logger.log(message=f"Download of {uri} succeedeed", log_level=3)
    return output_path
