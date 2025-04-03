#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.qgis.test_utils_application_folder
    # for specific test
    python -m unittest tests.qgis.test_utils_application_folder.TestToolbeltApplicationFolder.test_get_app_folder
"""

# standard library
import unittest
from os import getenv
from pathlib import Path

# project
from qtribu.toolbelt.application_folder import _posixify, get_app_dir

# ############################################################################
# ########## Classes #############
# ################################


class TestToolbeltApplicationFolder(unittest.TestCase):
    """Test toolbelt application folder module"""

    def test_get_app_folder(self):
        """Test application folder retrieval."""
        self.assertEqual(
            get_app_dir(dir_name="cache", roaming=False),
            Path(getenv("LOCALAPPDATA", Path.home())).joinpath(".geotribu/cache"),
        )

    def test_posixify(self):
        """Test posixify util."""
        self.assertEqual(_posixify("test PoSiXiFieD string"), "test-posixified-string")


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
