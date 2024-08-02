#! python3  # noqa: E265

"""Find application folder.

Inspired from Click: https://github.com/pallets/click/blob/14f735cf59618941cf2930e633eb77651b1dc7cb/src/click/utils.py#L449

"""

# ############################################################################
# ########## Imports ###############
# ##################################

# standard library
from functools import lru_cache
from os import getenv
from pathlib import Path

# ############################################################################
# ########## Functions #############
# ##################################


def _posixify(in_name: str) -> str:
    """Make sure a string is POSIX friendly.

    :param in_name: input string to posixify
    :type name: str

    :return: posixyfied string
    :rtype: str
    """
    return "-".join(in_name.split()).lower()


@lru_cache
def get_app_dir(
    dir_name: str, roaming: bool = True, app_prefix: str = ".geotribu"
) -> Path:
    """Get application directory, typically cache or config folder.  The default
        behavior is to return whatever is most appropriate for the operating system.

    :param dir_name: the directory name. Could be cache of config for example.
    :type dir_name: str
    :param roaming: controls if the folder should be roaming or not on Windows. Has no
        effect otherwise, defaults to True
    :type roaming: bool, optional
    :param app_prefix: application prefix, defaults to ".geotribu"
    :type app_prefix: str, optional

    :return: application folder path
    :rtype: Path

    :example:

        .. code-block:: python

            print(get_app_dir(dir_name="rss"))
            # Mac OS X: ~/Library/Application Support/.geotribu/rss
            # Unix: /home/<username>/.geotribu/rss
            # Windows (roaming): C:\\Users\\<user>\\AppData\\Roaming\\.geotribu\\rss
            print(get_app_dir(dir_name="rss", roaming=False))
            # Windows (not roaming): C:\\Users\\<user>\\AppData\\Local\\.geotribu\\rss
    """
    key = "APPDATA" if roaming else "LOCALAPPDATA"
    base_folder = Path(getenv(key, Path.home()))
    return base_folder.joinpath(f"{app_prefix}/{_posixify(dir_name)}")
