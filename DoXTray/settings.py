# some other useful imports
import os, sys
# interface with PyQt
from PyQt4 import QtCore, QtGui

class settings(QtCore.QSettings):
    def __init__(self, path=None):
        QtCore.QSettings.__init__(self)
        # default values
        self.setValue("TaskTableRowHighlight", self.value("TaskTableRowHighlight", "none"))
