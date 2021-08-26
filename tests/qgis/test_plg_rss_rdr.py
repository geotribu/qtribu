#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole tests
        python -m unittest tests.test_plg_rss_rdr
        # for specific test
        python -m unittest tests.test_plg_rss_rdr.TestRssReader.test_version_semver
"""

# standard library
import unittest

# project
from qtribu.logic import RssMiniReader

# ############################################################################
# ########## Classes #############
# ################################


class TestRssReader(unittest.TestCase):
    def test_rss_reader(self):
        """Test RSS reader basic behavior."""
        self.rss_rdr = RssMiniReader()


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
