# some other useful imports
import html, re, shlex, sys
# utility class import
from DoX.util import *
# edit window class import
from edit import *
# interface with PyQt
from PyQt4 import QtCore, QtGui

class listsWindow(QtGui.QMainWindow):
    def __init__(self, dox, settings, worker):
        QtGui.QMainWindow.__init__(self)
        self.dox = dox
        self.settings = settings
        self.worker = worker
        self.setWindowTitle("DoX: List tasks")
        self.setWindowIcon(QtGui.QIcon("check.png"))
        self.resize(1040, 600)
        self.setGeometry(QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter, self.size(),
                                                  QtGui.QDesktopWidget().availableGeometry()))
        # main widget
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.buildMain())
        mainWidget = QtGui.QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
        docks = self.buildDocks()
        for dock in docks:
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        # signal listeners
        self.connect(self.worker, QtCore.SIGNAL("refresh()"), self.refresh)
        # protocol handlers
        QtGui.QDesktopServices.setUrlHandler("dox", self.handleURL)
    def buildMain(self):
        # controls
        tables = []
        columns = [["#", "Task", "!", "Due", "Repeat", "Tags"], ["#", "Task", "!", "Due", "Tags"]]
        for i in range(2):
            table = QtGui.QTableWidget()
            table.setColumnCount(len(columns[i]))
            table.setHorizontalHeaderLabels(columns[i])
            table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            table.setShowGrid(False)
            table.verticalHeader().setVisible(False)
            table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            tables.append(table)
        self.taskTable, self.doneTable = tables
        self.taskTableLabel = QtGui.QLabel("No tasks to show under the current filters.  Why not <a href=\"dox://add\">add a new task</a>?")
        self.taskTableLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.taskTableLabel.setOpenExternalLinks(True)
        self.doneTableLabel = QtGui.QLabel("No tasks to show under the current filters.  Go and complete some!")
        self.doneTableLabel.setAlignment(QtCore.Qt.AlignCenter)
        # tabs
        self.listTabs = QtGui.QTabWidget()
        taskTab = QtGui.QWidget()
        doneTab = QtGui.QWidget()
        self.listTabs.addTab(taskTab, "To-do")
        self.listTabs.addTab(doneTab, "Done")
        # layouts
        taskLayout = QtGui.QVBoxLayout()
        taskLayout.addWidget(self.taskTable)
        taskLayout.addWidget(self.taskTableLabel)
        self.taskTableLabel.hide()
        taskTab.setLayout(taskLayout)
        doneLayout = QtGui.QVBoxLayout()
        doneLayout.addWidget(self.doneTable)
        doneLayout.addWidget(self.doneTableLabel)
        self.doneTableLabel.hide()
        doneTab.setLayout(doneLayout)
        # shortcuts
        switchMainTabs1 = QtGui.QShortcut(self)
        switchMainTabs1.setKey("Ctrl+Tab")
        switchMainTabs2 = QtGui.QShortcut(self)
        switchMainTabs2.setKey("Ctrl+Shift+Tab")
        # connections
        self.taskTable.itemSelectionChanged.connect(self.taskSelectionChanged)
        self.taskTable.customContextMenuRequested.connect(self.makeMenu)
        self.taskTable.cellDoubleClicked.connect(self.infoEditClicked)
        self.doneTable.itemSelectionChanged.connect(self.doneSelectionChanged)
        self.doneTable.customContextMenuRequested.connect(self.makeMenu)
        self.listTabs.currentChanged.connect(self.tabSwitched)
        switchMainTabs1.activated.connect(self.switchMainTab)
        switchMainTabs2.activated.connect(self.switchMainTab)
        # return new tabs
        return self.listTabs
    def buildDocks(self):
        # controls
        self.infoContent = QtGui.QLabel("Select a task on the left.")
        self.infoContent.setAlignment(QtCore.Qt.AlignCenter)
        self.infoContent.setOpenExternalLinks(True)
        self.infoContent.setWordWrap(True)
        self.infoDoneButton = QtGui.QPushButton("Done")
        self.infoDoneButton.setEnabled(False)
        self.infoEditButton = QtGui.QPushButton("Edit")
        self.infoEditButton.setEnabled(False)
        self.infoDeleteButton = QtGui.QPushButton("Delete")
        self.infoDeleteButton.setEnabled(False)
        sortALabel = QtGui.QLabel("Primary sort:")
        self.sortACombo = QtGui.QComboBox()
        self.sortACombo.addItems(["No sorting", "Task", "Priority", "Due", "Tags"])
        self.sortACheck = QtGui.QCheckBox("Descending")
        self.sortACheck.setEnabled(False)
        sortBLabel = QtGui.QLabel("Secondary sort:")
        self.sortBCombo = QtGui.QComboBox()
        self.sortBCombo.addItems(["No sorting", "Task", "Priority", "Due", "Tags"])
        self.sortBCombo.setEnabled(False)
        self.sortBCheck = QtGui.QCheckBox("Descending")
        self.sortBCheck.setEnabled(False)
        sortCLabel = QtGui.QLabel("Tertiary sort:")
        self.sortCCombo = QtGui.QComboBox()
        self.sortCCombo.addItems(["No sorting", "Task", "Priority", "Due", "Tags"])
        self.sortCCombo.setEnabled(False)
        self.sortCCheck = QtGui.QCheckBox("Descending")
        self.sortCCheck.setEnabled(False)
        sortMoveLabel = QtGui.QLabel("Move this task:")
        self.sortMoveUpButton = QtGui.QPushButton("Up")
        self.sortMoveUpButton.setEnabled(False)
        self.sortMoveDownButton = QtGui.QPushButton("Down")
        self.sortMoveDownButton.setEnabled(False)
        sortMovePosLabel = QtGui.QLabel("To position:")
        self.sortMovePosEdit = QtGui.QSpinBox()
        self.sortMovePosEdit.setMinimum(1)
        self.sortMovePosEdit.setEnabled(False)
        self.sortMovePosButton = QtGui.QPushButton("Go")
        self.sortMovePosButton.setEnabled(False)
        filterPriLabel = QtGui.QLabel("Restrict list to tasks with minimum priority:")
        self.filterPriCombo = QtGui.QComboBox()
        self.filterPriCombo.addItems(["Show all tasks", "At least medium", "High or critical", "Only critical"])
        filterDueLabel = QtGui.QLabel("Restrict list to tasks with due dates:")
        self.filterDueCombo = QtGui.QComboBox()
        self.filterDueCombo.addItems(["Show all tasks", "Due today", "Due tomorrow", "Due in the next week", "Overdue", "With a due date", "No due date"])
        filterTagLabel = QtGui.QLabel("Restrict list to tasks with assigned tags:")
        self.filterTagEdit = QtGui.QLineEdit()
        filterHighlightLabel = QtGui.QLabel("Highlight table rows by property:")
        self.filterHighlightCombo = QtGui.QComboBox()
        self.filterHighlightCombo.addItems(["None", "Priority", "Due date"])
        if self.settings.get("taskTableRowHighlight") == "pri":
            self.filterHighlightCombo.setCurrentIndex(1)
        elif self.settings.get("taskTableRowHighlight") == "due":
            self.filterHighlightCombo.setCurrentIndex(2)
        # layouts
        sortLayoutA = QtGui.QHBoxLayout()
        sortLayoutA.addWidget(sortALabel)
        sortLayoutA.addWidget(self.sortACombo)
        sortLayoutA.addWidget(self.sortACheck)
        sortLayoutB = QtGui.QHBoxLayout()
        sortLayoutB.addWidget(sortBLabel)
        sortLayoutB.addWidget(self.sortBCombo)
        sortLayoutB.addWidget(self.sortBCheck)
        sortLayoutC = QtGui.QHBoxLayout()
        sortLayoutC.addWidget(sortCLabel)
        sortLayoutC.addWidget(self.sortCCombo)
        sortLayoutC.addWidget(self.sortCCheck)
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
        cmdLayout.addWidget(self.infoEditButton)
        cmdLayout.addWidget(self.infoDeleteButton)
        taskLayout = QtGui.QVBoxLayout()
        taskLayout.addWidget(self.infoContent)
        taskLayout.addLayout(cmdLayout)
        sortLayout = QtGui.QVBoxLayout()
        sortLayout.addLayout(sortLayoutA)
        sortLayout.addLayout(sortLayoutB)
        sortLayout.addLayout(sortLayoutC)
        sortLayout.addLayout(moveLayout1)
        sortLayout.addLayout(moveLayout2)
        sortLayout.addStretch()
        filterHighlightLayout = QtGui.QHBoxLayout()
        filterHighlightLayout.addWidget(filterHighlightLabel)
        filterHighlightLayout.addWidget(self.filterHighlightCombo)
        filterLayout = QtGui.QVBoxLayout()
        filterLayout.addWidget(filterPriLabel)
        filterLayout.addWidget(self.filterPriCombo)
        filterLayout.addWidget(filterDueLabel)
        filterLayout.addWidget(self.filterDueCombo)
        filterLayout.addWidget(filterTagLabel)
        filterLayout.addWidget(self.filterTagEdit)
        filterLayout.addLayout(filterHighlightLayout)
        filterLayout.addStretch()
        # docks
        self.taskDock = QtGui.QDockWidget("Task")
        self.taskDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        taskWidget = QtGui.QWidget()
        taskWidget.setLayout(taskLayout)
        self.taskDock.setWidget(taskWidget)
        self.sortDock = QtGui.QDockWidget("Sort")
        self.sortDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        sortWidget = QtGui.QWidget()
        sortWidget.setLayout(sortLayout)
        self.sortDock.setWidget(sortWidget)
        self.filterDock = QtGui.QDockWidget("Filter")
        self.filterDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        filterWidget = QtGui.QWidget()
        filterWidget.setLayout(filterLayout)
        self.filterDock.setWidget(filterWidget)
        # connections
        self.infoDoneButton.clicked.connect(self.infoDoneClicked)
        self.infoEditButton.clicked.connect(self.infoEditClicked)
        self.infoDeleteButton.clicked.connect(self.infoDeleteClicked)
        self.sortACombo.currentIndexChanged.connect(self.sortComboChanged)
        self.sortACheck.stateChanged.connect(self.refresh)
        self.sortBCombo.currentIndexChanged.connect(self.sortComboChanged)
        self.sortBCheck.stateChanged.connect(self.refresh)
        self.sortCCombo.currentIndexChanged.connect(self.sortComboChanged)
        self.sortCCheck.stateChanged.connect(self.refresh)
        self.sortMoveUpButton.clicked.connect(self.sortMoveUpClicked)
        self.sortMoveDownButton.clicked.connect(self.sortMoveDownClicked)
        self.sortMovePosButton.clicked.connect(self.sortMovePosClicked)
        self.filterPriCombo.currentIndexChanged.connect(self.refresh)
        self.filterDueCombo.currentIndexChanged.connect(self.refresh)
        self.filterTagEdit.editingFinished.connect(self.refresh)
        self.filterHighlightCombo.currentIndexChanged.connect(self.filterHighlightChanged)
        # return new tabs
        return [self.taskDock, self.sortDock, self.filterDock]
    def refresh(self):
        # save current selections
        posList = self.tasksFromSelection()
        idList = list(map(lambda x: self.dox.posToId(x, self.listTabs.currentIndex() == 0), posList))
        # do tasks table first, then done table
        for table in [(self.taskTable, self.taskTableLabel, True), (self.doneTable, self.doneTableLabel, False)]:
            # flush table
            table[0].setRowCount(0)
            # fetch all tasks
            tasks = self.dox.getAllTasks(table[2])
            # apply priority filter
            pri = self.filterPriCombo.currentIndex()
            tasks = [x for x in tasks if x.pri >= pri]
            # apply due date filter
            due = self.filterDueCombo.currentIndex()
            today = datetime.datetime.today().date()
            # due today
            if due == 1:
                tasks = [x for x in tasks if x.due and x.due[0].date() <= today]
            # due tomorrow
            elif due == 2:
                tasks = [x for x in tasks if x.due and x.due[0].date() == today + datetime.timedelta(days=1)]
            # due in the next week
            elif due == 3:
                tasks = [x for x in tasks if x.due and today <= x.due[0].date() <= today + datetime.timedelta(days=7)]
            # overdue
            elif due == 4:
                tasks = [x for x in tasks if x.due and x.due[0].date() < today]
            # with a due date
            elif due == 5:
                tasks = [x for x in tasks if x.due]
            # no due date
            elif due == 6:
                tasks = [x for x in tasks if not x.due]
            # apply tag filter if set
            if self.filterTagEdit.text():
                tags = shlex.split(self.filterTagEdit.text())
                tasks = [x for x in tasks if set(x.tags).intersection(set(tags))]
            # if still tasks to show
            if len(tasks):
                # apply sort if set
                sorts = [(self.sortACombo.currentIndex(), self.sortACheck.isChecked()),
                         (self.sortBCombo.currentIndex(), self.sortBCheck.isChecked()),
                         (self.sortCCombo.currentIndex(), self.sortCCheck.isChecked())]
                # reverse sort arguments (so first sort field is applied last but appears first)
                sorts.reverse()
                # apply each sort in turn
                for sort in sorts:
                    if sort[0]:
                        fields = ["title", "pri", "due", "tags"]
                        field = fields[sort[0] - 1]
                        # sort with undefined items at bottom regardless of order
                        withField = sorted([x for x in tasks if not getattr(x, field) is None], key=(lambda x: getattr(x, field)), reverse=sort[1])
                        withoutField = [x for x in tasks if getattr(x, field) is None]
                        tasks = withField + withoutField
                # show table if previously hidden
                table[1].hide()
                table[0].show()
                # reallocate table
                table[0].setRowCount(len(tasks))
                # loop through tasks
                count = 0
                for taskObj in tasks:
                    # cell values
                    cells = [str(self.dox.idToPos(taskObj.id, table[2])), taskObj.title, str(taskObj.pri), prettyDue(taskObj.due) if taskObj.due else "<none>"]
                    # if tasks, add repeat column
                    if table[2]:
                        cells.append(prettyRepeat(taskObj.repeat) if taskObj.repeat else "<none>")
                    cells.append(", ".join(taskObj.tags) if len(taskObj.tags) else "<none>")
                    column = 0
                    # cell background colours
                    colours = ["dff0d8", "fcf8e3", "f2dede"]
                    colour = None
                    if self.settings.get("taskTableRowHighlight") == "pri" and taskObj.pri > 0:
                        colour = colours[taskObj.pri - 1]
                    elif self.settings.get("taskTableRowHighlight") == "due" and taskObj.due:
                        now = datetime.datetime.now()
                        today = datetime.datetime.combine(now.date(), datetime.time())
                        dueDay = datetime.datetime.combine(taskObj.due[0].date(), datetime.time())
                        # if task is due now
                        if (taskObj.due[1] and taskObj.due[0] < now) or (not taskObj.due[1] and taskObj.due[0] <= today):
                            colour = colours[2]
                        elif dueDay <= today + datetime.timedelta(days=1):
                            colour = colours[1]
                        else:
                            colour = colours[0]
                    for cell in cells:
                        # set each cell
                        cell =  QtGui.QTableWidgetItem(cell)
                        if colour:
                            cell.setData(QtCore.Qt.BackgroundRole, QtGui.QColor("#" + colour))
                        table[0].setItem(count, column, cell)
                        column += 1
                    count += 1
                # resize columns
                table[0].resizeColumnsToContents()
            else:
                # hide table
                table[0].hide()
                table[1].show()
        # update move position spinbox maximum value
        self.sortMovePosEdit.setMaximum(self.dox.getCount())
        # restore old selections
        posList = list(map(lambda x: self.dox.idToPos(x, self.listTabs.currentIndex() == 0), idList))
        # reselect rows
        for pos in posList:
            if pos:
                # -1 for 0-based row, 1-based ID
                self.taskTable.setCurrentCell(pos - 1, 0, QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
    def saveAndRefresh(self):
        # save tasks
        self.dox.saveTasks()
        # skip file monitor change detection
        self.emit(QtCore.SIGNAL("listsSaved()"))
        # refresh lists
        self.refresh()
    def makeMenu(self, loc):
        # menu shown when right-clicking rows in the table
        contextMenu = QtGui.QMenu()
        # different menus if selected tasks or not
        posList = self.tasksFromSelection()
        if len(posList) == 0:
            # not right-clicking on a task, show add option
            addAction = contextMenu.addAction("&Add task...")
            addAction.triggered.connect(self.triggerAddTask)
            contextMenu.setDefaultAction(addAction)
        else:
            # selected tasks
            if len(posList) == 1:
                titleAction = contextMenu.addAction(self.dox.getNthTask(posList[0], self.listTabs.currentIndex() == 0).title)
            else:
                titleAction = contextMenu.addAction("{} tasks selected".format(len(posList)))
            titleAction.setEnabled(False)
            contextMenu.addSeparator()
            # show edit option only for a single, incomplete task
            if self.listTabs.currentIndex() == 0 and len(posList) == 1:
                editAction = contextMenu.addAction("&Edit task")
                editAction.triggered.connect(self.infoEditClicked)
            doneAction = contextMenu.addAction("&Undo task{}".format("s" if len(posList) > 1 else "") if self.listTabs.currentIndex() == 1 else "Mark &done")
            doneAction.triggered.connect(self.infoDoneClicked)
            deleteAction = contextMenu.addAction("De&lete task{}".format("s" if len(posList) > 1 else ""))
            deleteAction.triggered.connect(self.infoDeleteClicked)
            # show move up/down if one continuous block selection, and no sorting enabled
            show = True
            count = -1
            for pos in sorted(posList):
                if count == -1:
                    count = pos
                elif pos > count + 1:
                    show = False
                else:
                    count += 1
            if show:
                contextMenu.addSeparator()
                moveUpAction = contextMenu.addAction("Move u&p")
                moveUpAction.triggered.connect(self.sortMoveUpClicked)
                moveDownAction = contextMenu.addAction("Move do&wn")
                moveDownAction.triggered.connect(self.sortMoveDownClicked)
            # default to editing tasks if available, else completing
            contextMenu.setDefaultAction(editAction if self.listTabs.currentIndex() == 0 and len(posList) == 1 else None)
        # show the menu
        table = self.doneTable if self.listTabs.currentIndex() == 1 else self.taskTable
        contextMenu.exec_(table.viewport().mapToGlobal(loc))
    def taskSelectionChanged(self):
        self.selectionChanged(True)
    def doneSelectionChanged(self):
        self.selectionChanged(False)
    def selectionChanged(self, isTasks):
        # get selected IDs
        posList = self.tasksFromSelection()
        # nothing selected
        if len(posList) == 0:
            self.infoContent.setText("Select a task on the left.")
            # disable all controls
            self.infoDoneButton.setEnabled(False)
            self.infoEditButton.setEnabled(False)
            self.infoDeleteButton.setEnabled(False)
            self.sortMoveUpButton.setEnabled(False)
            self.sortMoveDownButton.setEnabled(False)
            self.sortMovePosEdit.setEnabled(False)
            self.sortMovePosButton.setEnabled(False)
        # one row selected, show details
        elif len(posList) == 1:
            pos = posList[0]
            # fetch from correct table
            taskObj = self.dox.getNthTask(pos, isTasks)
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
            self.infoEditButton.setEnabled(isTasks)
            self.infoDeleteButton.setEnabled(True)
            self.sortMoveUpButton.setEnabled(isTasks and not pos == 1 and not self.sortACombo.currentIndex())
            self.sortMoveDownButton.setEnabled(isTasks and not pos == self.dox.getCount() and not self.sortACombo.currentIndex())
            self.sortMovePosEdit.setEnabled(isTasks and not self.sortACombo.currentIndex())
            self.sortMovePosButton.setEnabled(isTasks and not self.sortACombo.currentIndex())
            # update move position spinbox to current position
            self.sortMovePosEdit.setValue(pos)
        # multiple rows selected
        else:
            self.infoContent.setText("{} tasks selected.".format(len(posList)))
            # only enable multiple delete and completion
            self.infoDoneButton.setEnabled(True)
            self.infoEditButton.setEnabled(False)
            self.infoDeleteButton.setEnabled(True)
            # don't allow move to position
            self.sortMovePosEdit.setEnabled(False)
            self.sortMovePosButton.setEnabled(False)
            # enable move up/down if one continuous block selection, and no sorting enabled
            count = -1
            for pos in sorted(posList):
                if count == -1:
                    count = pos
                elif pos > count + 1:
                    self.sortMoveUpButton.setEnabled(False)
                    self.sortMoveDownButton.setEnabled(False)
                    return
                else:
                    count += 1
            self.sortMoveUpButton.setEnabled(isTasks and 1 not in posList and not self.sortACombo.currentIndex())
            self.sortMoveDownButton.setEnabled(isTasks and self.dox.getCount() not in posList and not self.sortACombo.currentIndex())
    def switchMainTab(self):
        # toggle tab index (1 - 1 = 0, 1 - 0 = 1)
        self.listTabs.setCurrentIndex(1 - self.listTabs.currentIndex())
    def tabSwitched(self, index):
        # clear selection on other table (i.e. not new selected one) on switch
        otherTable = self.taskTable if index == 1 else self.doneTable
        otherTable.clearSelection()
        # done tasks show an Undo button
        self.infoDoneButton.setText("Undo" if index == 1 else "Done")
    def triggerAddTask(self):
        self.emit(QtCore.SIGNAL("addTask()"))
    def infoDoneClicked(self):
        # get selected positions
        posList = self.tasksFromSelection()
        if len(posList):
            # use correct table
            isDone = self.listTabs.currentIndex() == 0
            # confirm if changing multiple tasks
            confirm = len(posList) == 1 or QtGui.QMessageBox.question(self, "DoX: {} tasks".format("Done" if isDone else "Undo"),
                                                                      "Are you sure you want to {}mark {} tasks as complete?".format("" if isDone else "un", len(posList)),
                                                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
            if confirm:
                # do in reverse to avoid ID conflicts
                for pos in sorted(posList, reverse=True):
                    if isDone:
                        self.dox.doneNthTask(pos)
                    else:
                        self.dox.undoNthTask(pos)
                # resave and refresh
                self.saveAndRefresh()
    def infoEditClicked(self):
        # row selected (option only available with single selections)
        posList = self.tasksFromSelection()
        if len(posList):
            pos = self.tasksFromSelection()[0]
            # make new edit window
            self.editWindow = editWindow(self.dox, pos)
            self.connect(self.editWindow, QtCore.SIGNAL("refresh()"), self.refresh)
            self.editWindow.connect(self, QtCore.SIGNAL("listsSaved()"), self.editWindow.refresh)
            self.editWindow.connect(self.worker, QtCore.SIGNAL("refresh()"), self.editWindow.refresh)
            self.editWindow.show()
    def infoDeleteClicked(self):
        # get selected positions
        posList = self.tasksFromSelection()
        if len(posList):
            # confirm deletion
            confirm = QtGui.QMessageBox.question(self, "DoX: Delete task" + ("" if len(posList) == 1 else "s"), "Are you sure you want to delete {}?".format("this task" if len(posList) == 1 else "these {} tasks".format(len(posList))),
                                                 QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if confirm == QtGui.QMessageBox.Yes:
                # do in reverse to avoid ID conflicts
                for pos in sorted(posList, reverse=True):
                    self.dox.deleteNthTask(pos, self.listTabs.currentIndex() == 0)
                # resave and refresh
                self.saveAndRefresh()
    def sortComboChanged(self):
        # read sort selections
        sort = [self.sortACombo.currentIndex(), self.sortBCombo.currentIndex(), self.sortCCombo.currentIndex()]
        # reset fields when higher sort disabled
        if not sort[0] or not sort[1] or not sort[2]:
            if not sort[0] or not sort[1]:
                if not sort[0]:
                    self.sortACheck.setChecked(False)
                    self.sortBCombo.setCurrentIndex(0)
                self.sortBCheck.setChecked(False)
                self.sortCCombo.setCurrentIndex(0)
            self.sortCCheck.setChecked(False)
        # enable if first sort set
        self.sortACheck.setEnabled(sort[0])
        self.sortBCombo.setEnabled(sort[0])
        # enable if first and second set
        self.sortBCheck.setEnabled(sort[0] and sort[1])
        self.sortCCombo.setEnabled(sort[0] and sort[1])
        # enable if all three set
        self.sortCCheck.setEnabled(sort[0] and sort[1] and sort[2])
        # refresh tables
        self.refresh()
    def sortMoveUpClicked(self):
        # list of rows selected
        posList = self.tasksFromSelection()
        # move each task up one, top to bottom
        for pos in sorted(posList):
            self.dox.moveNthTask(pos, pos - 1)
        # resave and refresh
        self.saveAndRefresh()
        # focus table
        self.taskTable.setFocus()
        # reselect rows
        for pos in posList:
            # -1 for move up, -1 for 0-based row, 1-based ID
            self.taskTable.setCurrentCell(pos - 2, 0, QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
    def sortMoveDownClicked(self):
        # list of rows selected
        posList = self.tasksFromSelection()
        # move each task down one, bottom to top
        for pos in sorted(posList, reverse=True):
            self.dox.moveNthTask(pos, pos + 1)
        # resave and refresh
        self.saveAndRefresh()
        # focus table
        self.taskTable.setFocus()
        # reselect rows
        for pos in posList:
            # +1 for move down, -1 for 0-based row, 1-based ID
            self.taskTable.setCurrentCell(pos, 0, QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
    def sortMovePosClicked(self):
        # row selected (option only available with single selections)
        pos = self.tasksFromSelection()[0]
        # read position from spinbox
        newPos = int(self.sortMovePosEdit.value())
        # if the values are different
        if not pos == newPos:
            # move the task
            self.dox.moveNthTask(pos, newPos)
            # resave and refresh
            self.saveAndRefresh()
            # focus table
            self.taskTable.setFocus()
            # reselect task at new position, -1 for 0-based row, 1-based ID
            self.taskTable.setCurrentCell(newPos - 1, 0, QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
    def filterHighlightChanged(self):
        # update highlighting setting
        highlight = "none"
        if self.filterHighlightCombo.currentIndex() == 1:
            highlight = "pri"
        elif self.filterHighlightCombo.currentIndex() == 2:
            highlight = "due"
        self.settings.set("taskTableRowHighlight", highlight)
        # refresh with new highlight
        self.refresh()
    def tasksFromSelection(self):
        # select from correct table
        table = self.doneTable if self.listTabs.currentIndex() == 1 else self.taskTable
        # list of rows selected
        posList = []
        for index in table.selectedIndexes():
            pos = int(table.item(index.row(), 0).text())
            if pos not in posList:
                posList.append(pos)
        return posList
    @QtCore.pyqtSlot(QtCore.QUrl)
    def handleURL(self, url):
        # add task request
        if url.host() == "add":
            self.triggerAddTask()
        # tag filter request
        elif url.host() == "tag":
            tag = url.path()[1:]
            # switch to filter tab
            self.controlTabs.setCurrentIndex(2)
            # append tag to current list
            if self.filterTagEdit.text():
                self.filterTagEdit.setText(self.filterTagEdit.text() + " " + quote(tag))
            else:
                self.filterTagEdit.setText(quote(tag))
    def closeEvent(self, event):
        # don't actually close - window is reused
        self.hide()
        event.ignore()
