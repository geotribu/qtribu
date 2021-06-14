from configparser import ConfigParser
from pathlib import Path, PurePath, PureWindowsPath
from os.path import normpath
from re import escape

# path
folder_path = Path(".").parent.resolve()
print(folder_path.resolve(), type(folder_path))

# purepath
folder_purepath = PurePath(str(folder_path))
print(folder_purepath, type(folder_purepath))

# purewindowspath
folder_purewinpath = PureWindowsPath(r"C:\Users\user\AppData\Roaming\QGIS\QGIS3\profiles\test_plg_qtribu\python\plugins\qtribu")
print(folder_purewinpath, type(folder_purewinpath))

# print(normpath(str(folder_path)))
# print(escape(str(folder_path)))
print(eval(repr(str(folder_path))))


# ini
ini_custom = ConfigParser()
ini_custom.optionxform = str
ini_custom["Customization"] = {
    "splash_path": str(folder_path),
    "splash_purepath": str(folder_purepath),
    "splash_winpath": str(folder_purewinpath),
    }


with open("test.ini", mode="w", encoding="UTF8") as configfile:
    ini_custom.write(configfile, space_around_delimiters=False)
