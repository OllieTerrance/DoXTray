# some other useful imports
import shlex, sys
# utility class import
from DoX.util import *
# recycle add window
from add import *
# interface with PyQt
from PyQt4 import QtCore, QtGui

class editWindow(addWindow):
    def __init__(self, dox, pos):
        # create add window
        addWindow.__init__(self, dox)
        self.taskObj = dox.getNthTask(pos)
        # replace title and button
        self.setWindowTitle("DoX: Edit task...")
        self.addButton.setText("&Edit")
        # add in warning block for task completed/deleted
        self.warningLabel = QtGui.QLabel("This task has been marked complete.")
        self.warningLabel.hide()
        self.warningUndoButton = QtGui.QPushButton("Undo")
        self.warningUndoButton.hide()
        self.warningLayout = QtGui.QHBoxLayout()
        self.warningLayout.addWidget(self.warningLabel)
        self.warningLayout.addWidget(self.warningUndoButton)
        self.mainLayout.addLayout(self.warningLayout)
        self.warningUndoButton.clicked.connect(self.warningUndo)
        # fill in fields
        self.stringEdit.setText(str(self.taskObj))
        self.fieldsDown()
    # catch refresh event
    def refresh(self):
        # clear any warnings
        if self.dox.getTask(self.taskObj.id):
            self.showWarning(0)
        # task has been marked complete
        elif self.dox.getTask(self.taskObj.id, False):
            self.showWarning(1)
        # task has been deleted
        else:
            self.showWarning(2)
    # show or hide the warning block
    def showWarning(self, type):
        # show the warning block
        if type:
            # show task marked complete warning
            if type == 1:
                self.warningLabel.setText("This task has been marked complete.")
                self.warningUndoButton.show()
                self.warningLabel.setStyleSheet("padding: 0 3px; background-color: #8F8;")
            # show task deleted warning
            else:
                self.warningLabel.setText("This task has been deleted.")
                self.warningUndoButton.hide()
                self.warningLabel.setStyleSheet("padding: 3px; background-color: #F88;")
            self.warningLabel.show()
            self.addButton.setEnabled(False)
        # hide it
        else:
            self.addButton.setEnabled(True)
            self.warningLabel.hide()
            self.warningLabel.setStyleSheet("padding: 3px;")
            self.warningUndoButton.hide()
    # undo mark task as complete
    def warningUndo(self):
        # restore task
        self.dox.undoTask(self.taskObj.id)
        self.showWarning(0)
        # resave
        self.dox.saveTasks()
        # trigger refresh for list window
        self.emit(QtCore.SIGNAL("refresh()"))
    # overload add method to edit instead
    def addTask(self):
        # fetch string and parse
        string = str(self.stringEdit.text())
        args = parseArgs(shlex.split(string))
        if len(args):
            # expand args tuple when passed to editTask
            self.dox.editTask(self.taskObj.id, *args[1:])
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
