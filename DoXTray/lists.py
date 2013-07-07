# some other useful imports
import html, sys
# add DoX core to path
sys.path.append("dox")
# main class import
from dox import *
# interface with PyQt
from PyQt4 import QtCore, QtGui

class lists(QtGui.QMainWindow):
    selectChangeOverride = False
    def __init__(self, dox, worker):
        QtGui.QMainWindow.__init__(self)
        self.dox = dox
        self.worker = worker
        self.setWindowTitle("DoX: List tasks")
        self.setWindowIcon(QtGui.QIcon("check.png"))
        self.resize(1040, 600)
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
        self.taskTable.setColumnCount(6)
        self.taskTable.setHorizontalHeaderLabels(["#", "Task", "!", "Due", "Repeat", "Tags"])
        self.taskTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.taskTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.taskTable.setShowGrid(False)
        # self.taskTable.setSortingEnabled(True)
        self.taskTable.verticalHeader().setVisible(False)
        self.doneTable = QtGui.QTableWidget()
        self.doneTable.setColumnCount(6)
        self.doneTable.setHorizontalHeaderLabels(["#", "Task", "!", "Due", "Repeat", "Tags"])
        self.doneTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.doneTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.doneTable.setShowGrid(False)
        # self.doneTable.setSortingEnabled(True)
        self.doneTable.verticalHeader().setVisible(False)
        self.taskInfo = QtGui.QLabel("Select a task on the left.")
        self.taskInfo.setAlignment(QtCore.Qt.AlignCenter)
        self.taskInfo.setWordWrap(True)
        # tabs
        listTabs = QtGui.QTabWidget()
        taskTab = QtGui.QWidget()
        doneTab = QtGui.QWidget()
        listTabs.addTab(taskTab, "To-do")
        listTabs.addTab(doneTab, "Done")
        infoTabs = QtGui.QTabWidget()
        infoTab = QtGui.QWidget()
        infoTabs.addTab(infoTab, "Task")
        infoTabs.setMaximumWidth(250)
        # layouts
        taskLayout = QtGui.QVBoxLayout()
        taskLayout.addWidget(self.taskTable)
        doneLayout = QtGui.QVBoxLayout()
        doneLayout.addWidget(self.doneTable)
        taskTab.setLayout(taskLayout)
        doneTab.setLayout(doneLayout)
        infoLayout = QtGui.QVBoxLayout()
        infoLayout.addWidget(self.taskInfo)
        infoTab.setLayout(infoLayout)
        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.addWidget(listTabs)
        self.mainLayout.addWidget(infoTabs)
        # connections
        self.taskTable.itemSelectionChanged.connect(self.taskSelectionChanged)
        self.doneTable.itemSelectionChanged.connect(self.doneSelectionChanged)
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
            cells = [str(taskObj.id), taskObj.title, str(taskObj.pri), prettyDue(taskObj.due) if taskObj.due else "<none>",
                     prettyRepeat(taskObj.repeat) if taskObj.repeat else "<none>", ", ".join(taskObj.tags)]
            column = 0
            for cell in cells:
                # set each cell
                self.taskTable.setItem(count, column, QtGui.QTableWidgetItem(cell))
                column += 1
            count += 1
        # resize columns
        self.taskTable.resizeColumnsToContents()
        # flush table
        self.doneTable.setRowCount(0)
        # reallocate table
        self.doneTable.setRowCount(len(self.dox.done))
        # loop through done tasks
        count = 0
        for taskObj in self.dox.done:
            # cell values
            cells = [str(taskObj.id), taskObj.title, str(taskObj.pri), prettyDue(taskObj.due) if taskObj.due else "<none>",
                     prettyRepeat(taskObj.repeat) if taskObj.repeat else "<none>", ", ".join(taskObj.tags)]
            column = 0
            for cell in cells:
                # set each cell
                self.doneTable.setItem(count, column, QtGui.QTableWidgetItem(cell))
                column += 1
            count += 1
        # resize columns
        self.doneTable.resizeColumnsToContents()
    def taskSelectionChanged(self):
        self.selectionChanged(True)
    def doneSelectionChanged(self):
        self.selectionChanged(False)
    def selectionChanged(self, isTasks):
        # if not setting selection programatically
        if not self.selectChangeOverride:
            # select from correct table
            table = self.taskTable if isTasks else self.doneTable
            # list of rows selected
            rows = []
            for i in table.selectedIndexes():
                if i.row() not in rows:
                    rows.append(i.row())
            # nothing selected
            if len(rows) == 0:
                self.taskInfo.setText("Select a task on the left.")
            # one row selected, show details
            elif len(rows) == 1:
                id = table.item(rows[0], 0).text()
                if isTasks:
                    taskObj = self.dox.getTask(int(id))
                else:
                    taskObj = self.dox.getDone(int(id))
                pris = ["Low", "Medium", "High", "Critical"]
                self.taskInfo.setText("""<b>{}</b><br/>
<br/>
{}Priority: {} ({}){}{}{}""".format(taskObj.title, html.escape(taskObj.desc).replace("\n", "<br/>\n") + "<br/>\n<br/>\n" if taskObj.desc else "",
                       pris[taskObj.pri], taskObj.pri, "<br/>\nDue: " + prettyDue(taskObj.due) if taskObj.due else "",
                       "<br/>\nRepeat: " + prettyRepeat(taskObj.repeat) if taskObj.repeat else "", "<br/>\n<br/>\n#" + " #".join(taskObj.tags) if taskObj.tags else ""))
            # multiple rows selected
            else:
                self.taskInfo.setText("{} tasks selected.".format(len(rows)))
    def closeEvent(self, event):
        # don't actually close - window is reused
        self.hide()
        event.ignore()
