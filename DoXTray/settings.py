# some other useful imports
import os, sys
# interface with PyQt
from PyQt4 import QtCore, QtGui

class settings:
    def __init__(self, path=None):
        self.path = path if path else self.makePath()
        # default values
        self.map = {
            "taskTableRowHighlight": "none"
        }
    def makePath(self):
        # use roaming AppData on Windows, or home directory on Mac/Linux
        return os.path.join(os.getenv("APPDATA"), "DoX Tray") if os.getenv("APPDATA") else os.path.join("~", ".DoXTray")
    def load(self):
        # no settings folder, create it
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        file = os.path.join(self.path, "settings.txt")
        # no settings file, create one
        if not os.path.exists(file):
            open(file, "w").close()
        settingsFile = open(file, "r")
        # read key/value pairs from each line
        for line in settingsFile:
            key, value = [x.strip() for x in line.split("=")]
            # add to map
            self.map[key] = value
        settingsFile.close()
    def save(self):
        # no settings folder, create it
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        file = os.path.join(self.path, "settings.txt")
        # write key value pairs to file
        settingsFile = open(file, "w")
        for key in self.map:
            settingsFile.write(key + " = " + str(self.map[key]) + "\n")
        settingsFile.close()
    def get(self, key):
        # shorthand to get a value
        return self.map[key]
    def set(self, key, value):
        # shorthand to set a value
        self.map[key] = value
