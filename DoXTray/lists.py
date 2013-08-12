# some other useful imports
import html, re, sys
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
        self.splitWidget = QtGui.QSplitter()
        self.splitWidget.addWidget(self.buildMain())
        self.splitWidget.addWidget(self.buildSide())
        self.splitMoved = False
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.splitWidget)
        mainWidget = QtGui.QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
        # signal listeners
        self.connect(self.worker, QtCore.SIGNAL("refresh()"), self.refresh)
        # protocol handlers
        QtGui.QDesktopServices.setUrlHandler("dox", self.handleURL)
    def buildMain(self):
        # controls
        tables = []
        for i in range(2):
            table = QtGui.QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["#", "Task", "!", "Due", "Repeat", "Tags"])
            table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            table.setShowGrid(False)
            table.verticalHeader().setVisible(False)
            tables.append(table)
        self.taskTable, self.doneTable = tables
        # tabs
        self.listTabs = QtGui.QTabWidget()
        taskTab = QtGui.QWidget()
        doneTab = QtGui.QWidget()
        self.listTabs.addTab(taskTab, "To-do")
        self.listTabs.addTab(doneTab, "Done")
        # layouts
        taskLayout = QtGui.QVBoxLayout()
        taskLayout.addWidget(self.taskTable)
        taskTab.setLayout(taskLayout)
        doneLayout = QtGui.QVBoxLayout()
        doneLayout.addWidget(self.doneTable)
        doneTab.setLayout(doneLayout)
        # shortcuts
        switchTabs1 = QtGui.QShortcut(self)
        switchTabs1.setKey("Ctrl+Tab")
        switchTabs2 = QtGui.QShortcut(self)
        switchTabs2.setKey("Ctrl+Shift+Tab")
        # connections
        self.taskTable.itemSelectionChanged.connect(self.taskSelectionChanged)
        self.doneTable.itemSelectionChanged.connect(self.doneSelectionChanged)
        self.listTabs.currentChanged.connect(self.tabSwitched)
        switchTabs1.activated.connect(self.switchTab)
        switchTabs2.activated.connect(self.switchTab)
        # return new tabs
        return self.listTabs
    def buildSide(self):
        # controls
        self.infoContent = QtGui.QLabel("Select a task on the left.")
        self.infoContent.setAlignment(QtCore.Qt.AlignCenter)
        self.infoContent.setOpenExternalLinks(True)
        self.infoContent.setWordWrap(True)
        self.infoDoneButton = QtGui.QPushButton("Done")
        self.infoDoneButton.setEnabled(False)
        self.infoMoveButton = QtGui.QPushButton("Move")
        self.infoMoveButton.setEnabled(False)
        self.infoEditButton = QtGui.QPushButton("Edit")
        self.infoEditButton.setEnabled(False)
        self.infoDeleteButton = QtGui.QPushButton("Delete")
        self.infoDeleteButton.setEnabled(False)
        sortMoveLabel = QtGui.QLabel("Move this task...")
        self.sortMoveUpButton = QtGui.QPushButton("Up")
        self.sortMoveUpButton.setEnabled(False)
        self.sortMoveDownButton = QtGui.QPushButton("Down")
        self.sortMoveDownButton.setEnabled(False)
        sortMovePosLabel = QtGui.QLabel("To position:")
        self.sortMovePosEdit = QtGui.QLineEdit()
        self.sortMovePosEdit.setEnabled(False)
        self.sortMovePosButton = QtGui.QPushButton("Go")
        self.sortMovePosButton.setEnabled(False)
        self.filterPriCheck = QtGui.QCheckBox("Restrict list to tasks with minimum priority:")
        self.filterPriCombo = QtGui.QComboBox()
        self.filterPriCombo.addItems(["Medium (1)", "High (2)", "Critical (3)"])
        self.filterPriCombo.setEnabled(False)
        self.filterTagCheck = QtGui.QCheckBox("Restrict list to tasks with assigned tags:")
        self.filterTagEdit = QtGui.QLineEdit()
        self.filterTagEdit.setEnabled(False)
        # tabs
        self.controlTabs = QtGui.QTabWidget()
        infoTab = QtGui.QWidget()
        sortTab = QtGui.QWidget()
        filterTab = QtGui.QWidget()
        self.controlTabs.addTab(infoTab, "Task")
        self.controlTabs.addTab(sortTab, "Sort")
        self.controlTabs.addTab(filterTab, "Filter")
        # layouts
        moveLayout1 = QtGui.QHBoxLayout()
        moveLayout1.addWidget(sortMoveLabel)
        moveLayout1.addWidget(self.sortMoveUpButton)
        moveLayout1.addWidget(self.sortMoveDownButton)
        moveLayout2 = QtGui.QHBoxLayout()
        moveLayout2.addWidget(sortMovePosLabel)
        moveLayout2.addWidget(self.sortMovePosEdit)
        moveLayout2.addWidget(self.sortMovePosButton)
        cmdLayout = QtGui.QHBoxLayout()
        cmdLayout.addWidget(self.infoDoneButton)
        cmdLayout.addWidget(self.infoMoveButton)
        cmdLayout.addWidget(self.infoEditButton)
        cmdLayout.addWidget(self.infoDeleteButton)
        self.infoLayout = QtGui.QVBoxLayout()
        self.infoLayout.addWidget(self.infoContent)
        self.infoLayout.addLayout(cmdLayout)
        infoTab.setLayout(self.infoLayout)
        sortLayout = QtGui.QVBoxLayout()
        sortLayout.addLayout(moveLayout1)
        sortLayout.addLayout(moveLayout2)
        sortTab.setLayout(sortLayout)
        filterLayout = QtGui.QVBoxLayout()
        filterLayout.addWidget(self.filterPriCheck)
        filterLayout.addWidget(self.filterPriCombo)
        filterLayout.addWidget(self.filterTagCheck)
        filterLayout.addWidget(self.filterTagEdit)
        filterTab.setLayout(filterLayout)
        # connections
        self.infoDoneButton.clicked.connect(self.infoDoneClicked)
        self.infoEditButton.clicked.connect(self.infoEditClicked)
        self.infoDeleteButton.clicked.connect(self.infoDeleteClicked)
        self.sortMoveUpButton.clicked.connect(self.sortMoveUpClicked)
        self.sortMoveDownButton.clicked.connect(self.sortMoveDownClicked)
        self.filterPriCheck.toggled.connect(self.filterPriToggled)
        self.filterTagCheck.toggled.connect(self.filterTagToggled)
        # return new tabs
        return self.controlTabs
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
                     prettyRepeat(taskObj.repeat) if taskObj.repeat else "<none>", ", ".join(taskObj.tags) if len(taskObj.tags) else "<none>"]
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
                     prettyRepeat(taskObj.repeat) if taskObj.repeat else "<none>", ", ".join(taskObj.tags) if len(taskObj.tags) else "<none>"]
            column = 0
            for cell in cells:
                # set each cell
                self.doneTable.setItem(count, column, QtGui.QTableWidgetItem(cell))
                column += 1
            count += 1
        # resize columns
        self.doneTable.resizeColumnsToContents()
    def saveAndRefresh(self):
        # save tasks
        self.dox.saveTasks()
        # skip file monitor change detection
        self.emit(QtCore.SIGNAL("listsSaved()"))
        # refresh lists
        self.refresh()
    def taskSelectionChanged(self):
        self.selectionChanged(True)
    def doneSelectionChanged(self):
        self.selectionChanged(False)
    def selectionChanged(self, isTasks):
        # if not setting selection programatically
        if not self.selectChangeOverride:
            # get selected IDs
            ids = self.tasksFromSelection()
            # nothing selected
            if len(ids) == 0:
                self.infoContent.setText("Select a task on the left.")
                # disable all controls
                self.infoDoneButton.setEnabled(False)
                self.infoMoveButton.setEnabled(False)
                self.infoEditButton.setEnabled(False)
                self.infoDeleteButton.setEnabled(False)
                self.sortMoveUpButton.setEnabled(False)
                self.sortMoveDownButton.setEnabled(False)
            # one row selected, show details
            elif len(ids) == 1:
                id = ids[0]
                # fetch from correct table
                taskObj = self.dox.getTask(int(id), isTasks)
                pris = ["Low", "Medium", "High", "Critical"]
                # convert a URL into an <a> tag with correct link
                def linkify(match):
                    # group 0 is entire match
                    href = match.group(0)
                    # no protocol, default to http://
                    if not match.group(1):
                        href = "http://" + href
                    # return <a> tag
                    return "<a href=\"" + href.replace("\"", "%22") + "\">" + html.escape(match.group(0)) + "</a>"
                # linkify all URLs, including ones that look like links (e.g. "foo.com")
                descWrap = re.sub("([a-z]+://)?([a-z\-\+]+\.)+[a-z]{2,6}([/#?]\S*[^\.,\s\[\]\(\)])*", linkify, taskObj.desc, flags=re.IGNORECASE)
                # HTML new lines
                descWrap = descWrap.replace("\n", "<br/>")
                # link tags to internal protocol for tag filtering
                tagWrap = ["<a href=\"dox://tag/{0}\">{0}</a>".format(x) for x in taskObj.tags]
                # set new content
                self.infoContent.setText("<b>{}</b><br/><br/>{}Priority: {} ({}){}{}{}".format(taskObj.title,
                                                                                               descWrap + "<br/><br/>" if descWrap else "",
                                                                                               pris[taskObj.pri], taskObj.pri,
                                                                                               "<br/>Due: " + prettyDue(taskObj.due) if taskObj.due else "",
                                                                                               "<br/>Repeat: " + prettyRepeat(taskObj.repeat) if taskObj.repeat else "",
                                                                                               "<br/><br/>" + "  ".join(tagWrap) if tagWrap else ""))
                # enable multiple delete and completion, plus others if tasks (not done)
                self.infoDoneButton.setEnabled(True)
                self.infoMoveButton.setEnabled(isTasks)
                self.infoEditButton.setEnabled(isTasks)
                self.infoDeleteButton.setEnabled(True)
                self.sortMoveUpButton.setEnabled(isTasks and 1 not in ids)
                self.sortMoveDownButton.setEnabled(isTasks and self.dox.getCount() not in ids)
            # multiple rows selected
            else:
                self.infoContent.setText("{} tasks selected.".format(len(ids)))
                # only enable multiple delete and completion
                self.infoDoneButton.setEnabled(True)
                self.infoMoveButton.setEnabled(False)
                self.infoEditButton.setEnabled(False)
                self.infoDeleteButton.setEnabled(True)
                # enable move if one continuous block selection
                count = -1
                for id in ids:
                    if count == -1:
                        count = id
                    elif id > count + 1:
                        self.sortMoveUpButton.setEnabled(False)
                        self.sortMoveDownButton.setEnabled(False)
                        return
                    else:
                        count += 1
                self.sortMoveUpButton.setEnabled(isTasks and 1 not in ids)
                self.sortMoveDownButton.setEnabled(isTasks and self.dox.getCount() not in ids)
    def switchTab(self):
        # toggle tab index (1 - 1 = 0, 1 - 0 = 1)
        self.listTabs.setCurrentIndex(1 - self.listTabs.currentIndex())
    def tabSwitched(self, index):
        # clear selection on other table (i.e. not new selected one) on switch
        otherTable = self.taskTable if index == 1 else self.doneTable
        otherTable.clearSelection()
        # done tasks show an Undo button
        self.infoDoneButton.setText("Undo" if index == 1 else "Done")
    def infoDoneClicked(self):
        # get selected IDs
        ids = self.tasksFromSelection()
        # use correct table
        isDone = self.listTabs.currentIndex() == 0
        # confirm if changing multiple tasks
        confirm = len(ids) == 1 or QtGui.QMessageBox.question(self, "DoX: {} tasks".format("Done" if isDone else "Undo"),
                                                              "Are you sure you want to {}mark {} tasks as complete?".format("" if isDone else "un", len(ids)),
                                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
        if confirm:
            # do in reverse to avoid ID conflicts
            for id in sorted(ids, reverse=True):
                if isDone:
                    self.dox.doneTask(id)
                else:
                    self.dox.undoTask(id)
            # resave and refresh
            self.saveAndRefresh()
    def infoEditClicked(self):
        pass
    def infoDeleteClicked(self):
        # get selected IDs
        ids = self.tasksFromSelection()
        # confirm deletion
        confirm = QtGui.QMessageBox.question(self, "DoX: Delete task", "Are you sure you want to delete {}?".format("this task" if len(ids) == 1 else "these {} tasks".format(len(ids))),
                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if confirm == QtGui.QMessageBox.Yes:
            # do in reverse to avoid ID conflicts
            for id in sorted(ids, reverse=True):
                self.dox.deleteTask(id, self.listTabs.currentIndex() == 0)
            # resave and refresh
            self.saveAndRefresh()
    def sortMoveUpClicked(self):
        # list of rows selected
        ids = self.tasksFromSelection()
        # sort into ID order
        ids.sort()
        # move each task up one
        for id in ids:
            self.dox.moveTask(id, id - 1, False if self.listTabs.currentIndex() == 1 else True)
        # resave and refresh
        self.saveAndRefresh()
        # focus table
        self.taskTable.setFocus()
        # reselect rows
        for id in ids:
            # -1 for move up, -1 for 0-based row, 1-based id
            self.taskTable.setCurrentCell(id - 2, 0, QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
    def sortMoveDownClicked(self):
        # list of rows selected
        ids = self.tasksFromSelection()
        # sort into reverse ID order
        ids.sort(reverse=True)
        # move each task down one
        for id in ids:
            self.dox.moveTask(id, id + 1, False if self.listTabs.currentIndex() == 1 else True)
        # resave and refresh
        self.saveAndRefresh()
        # focus table
        self.taskTable.setFocus()
        # reselect rows
        for id in ids:
            # +1 for move down, -1 for 0-based row, 1-based id
            self.taskTable.setCurrentCell(id, 0, QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
    def filterPriToggled(self, checked):
        self.filterPriCombo.setEnabled(checked)
    def filterTagToggled(self, checked):
        self.filterTagEdit.setEnabled(checked)
    def tasksFromSelection(self):
        # select from correct table
        table = self.doneTable if self.listTabs.currentIndex() == 1 else self.taskTable
        # list of rows selected
        ids = []
        for i in table.selectedIndexes():
            id = int(table.item(i.row(), 0).text())
            if id not in ids:
                ids.append(id)
        return ids
    @QtCore.pyqtSlot(QtCore.QUrl)
    def handleURL(self, url):
        # tag filter request
        if url.host() == "tag":
            tag = url.path()[1:]
            # switch to filter tab
            self.controlTabs.setCurrentIndex(2)
            # enable filtering by tag
            self.filterTagCheck.setChecked(True)
            # append tag to current list
            if self.filterTagEdit.text():
                self.filterTagEdit.setText(self.filterTagEdit.text() + " " + quote(tag))
            else:
                self.filterTagEdit.setText(quote(tag))
    def closeEvent(self, event):
        # don't actually close - window is reused
        self.hide()
        event.ignore()