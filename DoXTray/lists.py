# some other useful imports
import sys
# add DoX core to path
sys.path.append("dox")
# main class import
from dox import *
# interface with PyQt
from PyQt4 import QtCore, QtGui

class lists(QtGui.QMainWindow):
    def __init__(self, dox, worker):
        QtGui.QMainWindow.__init__(self)
        self.dox = dox
        self.worker = worker
        self.setWindowTitle("DoX: List tasks")
        self.setWindowIcon(QtGui.QIcon("check.png"))
        self.resize(600, 350)
        self.setGeometry(QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter, self.size(),
                                                  QtGui.QDesktopWidget().availableGeometry()))
        # main widget
        self.mainWidget = QtGui.QWidget()
        self.mainWidget.setLayout(self.buildMain())
        self.setCentralWidget(self.mainWidget)
        # signal listeners
        self.connect(self.worker, QtCore.SIGNAL("refresh()"), self.refresh)
    def buildMain(self):
        # controls
        self.taskTable = QtGui.QTableWidget()
        self.taskTable.setColumnCount(5)
        self.taskTable.setHorizontalHeaderLabels(["Task", "Priority", "Due", "Repeat", "Tags"])
        self.taskTable.setSortingEnabled(True)
        self.doneTable = QtGui.QTableWidget()
        self.doneTable.setColumnCount(5)
        self.doneTable.setHorizontalHeaderLabels(["Task", "Priority", "Due", "Repeat", "Tags"])
        self.doneTable.setSortingEnabled(True)
        # tabs
        tabs = QtGui.QTabWidget()
        taskTab = QtGui.QWidget()	
        doneTab = QtGui.QWidget()
        tabs.addTab(taskTab, "To-do")
        tabs.addTab(doneTab, "Done")
        # layouts
        taskLayout = QtGui.QVBoxLayout()
        taskLayout.addWidget(self.taskTable)
        doneLayout = QtGui.QVBoxLayout()
        doneLayout.addWidget(self.doneTable)
        taskTab.setLayout(taskLayout)
        doneTab.setLayout(doneLayout)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(tabs)
        # return new layout
        return self.mainLayout
    def refresh(self):
        # flush table
        self.taskTable.setRowCount(0)
        # reallocate table
        self.taskTable.setRowCount(len(self.dox.tasks))
        # loop through tasks
        count = 0
        for taskObj in self.dox.tasks:
            # cell values
            cells = [taskObj.title, str(taskObj.pri), prettyDue(taskObj.due) if taskObj.due else "<none>",
                     prettyRepeat(taskObj.repeat) if taskObj.repeat else "<none>", ", ".join(taskObj.tags)]
            column = 0
            for cell in cells:
                # set each cell
                self.taskTable.setItem(count, column, QtGui.QTableWidgetItem(cell))
                column += 1
            count += 1
        # flush table
        self.doneTable.setRowCount(0)
        # reallocate table
        self.doneTable.setRowCount(len(self.dox.done))
        # loop through done tasks
        count = 0
        for taskObj in self.dox.done:
            # cell values
            cells = [taskObj.title, str(taskObj.pri), prettyDue(taskObj.due) if taskObj.due else "<none>",
                     prettyRepeat(taskObj.repeat) if taskObj.repeat else "<none>", ", ".join(taskObj.tags)]
            column = 0
            for cell in cells:
                # set each cell
                self.doneTable.setItem(count, column, QtGui.QTableWidgetItem(cell))
                column += 1
            count += 1
        # resize columns
        self.taskTable.resizeColumnsToContents()
        self.doneTable.resizeColumnsToContents()
    def closeEvent(self, event):
        # don't actually close - window is reused
        self.hide()
        event.ignore()
