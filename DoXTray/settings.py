# some other useful imports
import os, sys
# interface with PyQt
from PyQt4 import QtCore, QtGui

class settings(QtCore.QSettings):
    def __init__(self, path=None):
        QtCore.QSettings.__init__(self)
        # default values
        self.setValue("TaskTableRowHighlight", self.value("TaskTableRowHighlight", "none"))
        self.setValue("TaskTableSortAType", self.value("TaskTableSortAType", "none"))
        self.setValue("TaskTableSortADesc", self.value("TaskTableSortADesc", False))
        self.setValue("TaskTableSortBType", self.value("TaskTableSortBType", "none"))
        self.setValue("TaskTableSortBDesc", self.value("TaskTableSortBDesc", False))
        self.setValue("TaskTableSortCType", self.value("TaskTableSortCType", "none"))
        self.setValue("TaskTableSortCDesc", self.value("TaskTableSortCDesc", False))
