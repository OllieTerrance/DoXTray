# some other useful imports
import shlex, sys
# add DoX core to path
sys.path.append("dox")
# main class import
from dox import *
# recycle add window
from add import *
# interface with PyQt
from PyQt4 import QtCore, QtGui

class edit(add):
    def __init__(self, dox, id):
        # create add window
        add.__init__(self, dox)
        self.taskObj = dox.getTask(id)
        # replace title and button
        self.setWindowTitle("DoX: Edit task...")
        self.addButton.setText("&Edit")
        # fill in fields
        self.stringEdit.setText(str(self.taskObj))
        self.fieldsDown()
    # overload add method to edit instead
    def addTask(self):
        # fetch string and parse
        string = str(self.stringEdit.text())
        args = parseArgs(shlex.split(string))
        if len(args):
            # expand args tuple when passed to editTask
            self.dox.editTask(self.taskObj.id, *args)
            # resave
            self.dox.saveTasks()
            # trigger refresh for list window
            self.emit(QtCore.SIGNAL("refresh()"))
            # show notification
            self.emit(QtCore.SIGNAL("info(QString, QString)"), args[0], "Task updated successfully.")
        # close window now
        self.close()
    # overload close event to actually close window this time
    def closeEvent(self, event):
        event.accept()