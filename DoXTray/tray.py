# some other useful imports
import datetime, os, shlex, sys, time, webbrowser
# add DoX core to path
sys.path.append("dox")
# main class import
from dox import *
# interface with PyQt
from PyQt4 import QtCore, QtGui

class worker(QtCore.QThread):
    def __init__(self, dox):
        QtCore.QThread.__init__(self)
        # connect to API
        self.dox = dox
        # load tasks
        self.dox.loadTasks()
        # set last read time to now
        self.fileLastMod = datetime.datetime.now()
        # trigger refresh for list window
        self.emit(QtCore.SIGNAL("refresh()"))
        # empty list of past notifications
        self.notified = []
    def run(self):
        while True:
            # tasks list has been modified since last check
            if self.dox.tasksFileLastMod() > self.fileLastMod:
                # reload tasks from file
                self.dox.loadTasks()
                # update last mod. time
                self.fileLastMod = self.dox.tasksFileLastMod()
                # trigger refresh for list window
                self.emit(QtCore.SIGNAL("refresh()"))
            now = datetime.datetime.now()
            today = datetime.datetime.combine(now.date(), datetime.time())
            # loop all tasks
            for taskObj in self.dox.tasks:
                # if task is due now, and hasn't been notified about yet
                if taskObj not in self.notified and taskObj.due and ((taskObj.due[1] and taskObj.due[0] < now) or (not taskObj.due[1] and taskObj.due[0] <= today)):
                    # popup alert
                    self.emit(QtCore.SIGNAL("warning(QString, QString)"), taskObj.title, (taskObj.desc if taskObj.desc else "Due now!"))
                    # add to known notified list
                    self.notified.append(taskObj)
                    break
            # remove tasks from notified that don't exist
            self.notified = [x for x in self.notified if x in self.dox.tasks]
            # sleep for a bit
            time.sleep(5)
        return

class add(QtGui.QMainWindow):
    def __init__(self, dox):
        QtGui.QMainWindow.__init__(self)
        self.dox = dox
        self.setWindowTitle("DoX: Add task...")
        self.setWindowIcon(QtGui.QIcon("check.png"))
        self.resize(300, 250)
        self.setGeometry(QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter, self.size(),
                                                  QtGui.QDesktopWidget().availableGeometry()))
        # main widget
        self.mainWidget = QtGui.QWidget()
        self.mainWidget.setLayout(self.buildMain())
        self.setCentralWidget(self.mainWidget)
    def buildMain(self):
        # controls
        self.stringEdit = QtGui.QLineEdit()
        self.stringEdit.setPlaceholderText("\"Feed the cat\" !2 @tomorrow|13:30 &daily* #Home #Cat")
        self.addButton = QtGui.QPushButton("&Add")
        self.addButton.setAutoDefault(True)
        self.addButton.setDefault(True)
        self.cancelButton = QtGui.QPushButton("&Cancel")
        # layouts
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.cancelButton)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.stringEdit)
        self.mainLayout.addLayout(buttonLayout)
        self.mainLayout.addLayout(self.buildFields())
        # connections
        self.stringEdit.editingFinished.connect(self.fieldsDown)
        self.addButton.clicked.connect(self.addTask)
        self.cancelButton.clicked.connect(self.closeWindow)
        # return new layout
        return self.mainLayout
    def buildFields(self):
        # controls
        label = QtGui.QLabel("...or enter the individual details.")
        self.titleEdit = QtGui.QLineEdit()
        self.titleEdit.setPlaceholderText("Feed the cat")
        self.descEdit = QtGui.QTextEdit()
        self.descEdit.setAcceptRichText(False)
        self.priCombo = QtGui.QComboBox()
        self.priCombo.addItems(["0 (Low)", "1 (Medium)", "2 (High)", "3 (Critical)"])
        self.dueDateEdit = QtGui.QLineEdit()
        self.dueDateEdit.setPlaceholderText("tomorrow")
        self.dueTimeEdit = QtGui.QLineEdit()
        self.dueTimeEdit.setPlaceholderText("13:30")
        self.repeatCombo = QtGui.QComboBox()
        self.repeatCombo.addItems(["No repeat", "Daily", "Weekly", "Fortnightly", "Custom..."])
        self.repeatEdit = QtGui.QLineEdit()
        self.repeatEdit.setEnabled(False)
        self.repeatCheck = QtGui.QCheckBox("From done?")
        self.repeatCheck.setChecked(True)
        self.repeatCheck.setEnabled(False)
        self.tagsEdit = QtGui.QLineEdit()
        self.tagsEdit.setPlaceholderText("Home Cat")
        # layouts
        dueLayout = QtGui.QHBoxLayout()
        dueLayout.addWidget(self.dueDateEdit)
        dueLayout.addWidget(self.dueTimeEdit)
        repeatLayout = QtGui.QHBoxLayout()
        repeatLayout.addWidget(self.repeatCombo)
        repeatLayout.addWidget(self.repeatEdit)
        repeatLayout.addWidget(self.repeatCheck)
        fieldsLayout = QtGui.QFormLayout()
        fieldsLayout.setLabelAlignment(QtCore.Qt.AlignRight);
        fieldsLayout.addRow("", self.titleEdit)
        fieldsLayout.addRow("~", self.descEdit)
        fieldsLayout.addRow("!", self.priCombo)
        fieldsLayout.addRow("@", dueLayout)
        fieldsLayout.addRow("&", repeatLayout)
        fieldsLayout.addRow("#", self.tagsEdit)
        # connections
        self.titleEdit.textEdited.connect(self.fieldsUp)
        self.descEdit.textChanged.connect(self.fieldsUp)
        self.priCombo.currentIndexChanged.connect(self.fieldsUp)
        self.dueDateEdit.editingFinished.connect(self.dueDateEditFinished)
        self.dueTimeEdit.editingFinished.connect(self.dueTimeEditFinished)
        self.repeatEdit.editingFinished.connect(self.repeatEditFinished)
        self.repeatCombo.currentIndexChanged.connect(self.repeatComboChanged)
        self.repeatCheck.stateChanged.connect(self.fieldsUp)
        self.tagsEdit.textEdited.connect(self.fieldsUp)
        self.tagsEdit.editingFinished.connect(self.tagsEditFinished)
        # return new layout
        return fieldsLayout
    def dueDateEditFinished(self):
        # call main handler, knowing the date was edited
        self.dueEditFinished(True)
    def dueTimeEditFinished(self):
        # call main handler, knowing the time was edited
        self.dueEditFinished(False)
    def dueEditFinished(self, isDate):
        date = str(self.dueDateEdit.text())
        time = str(self.dueTimeEdit.text())
        # time set but no date
        if time and not date:
            # if removed the date, also remove the time
            if isDate:
                time = ""
            # if added the time, also add the date (set to today)
            else:
                date = "today"
        # parse given values
        due = parseDateTime(date, time)
        # if a valid date
        if due:
            # set to actual date string
            self.dueDateEdit.setText(due[0].strftime("%d/%m/%Y"))
            # if a valid time as well
            if due[1]:
                # set to actual time string
                self.dueTimeEdit.setText(due[0].strftime("%H:%M:%S"))
            else:
                # invalid, clear field
                self.dueTimeEdit.setText("")
        # invalid, clear fields
        else:
            self.dueDateEdit.setText("")
            self.dueTimeEdit.setText("")
        # update string field
        self.fieldsUp()
    def repeatComboChanged(self, index):
        # enable edit field if combo on custom
        self.repeatEdit.setEnabled(index == 4)
        self.repeatEdit.setText("")
        # set edit box to values for combo box
        if index == 1:
            self.repeatEdit.setText("1")
        elif index == 2:
            self.repeatEdit.setText("7")
        elif index == 3:
            self.repeatEdit.setText("14")
        # enable checkbox if repeat is enabled
        self.repeatCheck.setEnabled(index)
        # switching to custom, focus edit field
        if index == 4:
            self.repeatEdit.setFocus()
        else:
            # update string field
            self.fieldsUp()
    def repeatEditFinished(self):
        value = str(self.repeatEdit.text())
        # test if value is valid
        if value:
            try:
                value = int(value)
                # can't be zero or below
                if value < 1:
                    raise ValueError
                # if worded value, switch to combo value
                elif value == 1:
                    self.repeatCombo.setCurrentIndex(1)
                elif value == 7:
                    self.repeatCombo.setCurrentIndex(2)
                elif value == 14:
                    self.repeatCombo.setCurrentIndex(3)
                else:
                    # update string field
                    self.fieldsUp(True)
            # invalid, clear and re-enter
            except ValueError:
                self.repeatEdit.setText("")
                self.repeatEdit.setFocus()
        # left blank, revert to no repeat
        else:
            self.repeatCombo.setCurrentIndex(0)
    def tagsEditFinished(self):
        try:
            # attempt to split tags
            shlex.split(str(self.tagsEdit.text()))
        except ValueError:
            # can't parse, refocus until complete
            self.tagsEdit.setFocus()
    def fieldsUp(self, isRepeat=False):
        if not isRepeat:
            # clear status of repeat edit if there is one
            self.repeatEditFinished()
        # fetch values
        title = str(self.titleEdit.text())
        desc = self.descEdit.toPlainText()
        pri = self.priCombo.currentIndex()
        due = None
        dueStr = str(self.dueDateEdit.text())
        # assuming a valid date (as parsed in dueEditFinished)
        if dueStr:
            due = parseDateTime(dueStr, str(self.dueTimeEdit.text()))
        repeat = None
        repeatStr = str(self.repeatEdit.text())
        # assuming valid (either set from combo or parsed in repeatEditFinished)
        if repeatStr.isdigit():
            repeat = (int(repeatStr), not self.repeatCheck.isChecked())
        try:
            # attempt to split tags
            tags = shlex.split(str(self.tagsEdit.text()))
        except ValueError:
            # can't parse, don't set
            tags = []
        self.stringEdit.setText(formatArgs(title, desc, pri, due, repeat, tags))
    def fieldsDown(self):
        try:
            args = shlex.split(str(self.stringEdit.text()))
        except:
            print("Parse error!")
            args = []
        title, desc, pri, due, repeat, tags = parseArgs(args)
        self.titleEdit.setText(title)
        self.descEdit.setText(desc)
        self.priCombo.setCurrentIndex(pri)
        self.dueDateEdit.setText("")
        self.dueTimeEdit.setText("")
        if due:
            self.dueDateEdit.setText(due[0].strftime("%d/%m/%Y"))
            self.dueTimeEdit.setText(due[0].strftime("%H:%M:%S" if due[1] else ""))
        self.repeatCombo.setCurrentIndex(0)
        self.repeatEdit.setText("")
        self.repeatEdit.setEnabled(False)
        if repeat:
            if repeat[0] == 1:
                self.repeatCombo.setCurrentIndex(1)
            elif repeat[0] == 7:
                self.repeatCombo.setCurrentIndex(2)
            elif repeat[0] == 14:
                self.repeatCombo.setCurrentIndex(3)
            else:
                self.repeatCombo.setCurrentIndex(4)
                self.repeatEdit.setEnabled(True)
            self.repeatCheck.setChecked(True)
            if repeat[1]:
                self.repeatCheck.setChecked(False)
        self.tagsEdit.setText(" ".join([quote(x) for x in tags]))
    def addTask(self):
        # fetch string and parse
        string = str(self.stringEdit.text())
        args = parseArgs(shlex.split(string))
        if len(args):
            # expand args tuple when passed to addTask
            self.dox.addTask(*args)
            # resave
            self.dox.saveTasks()
            # show notification
            self.emit(QtCore.SIGNAL("info(QString, QString)"), args[0], "Task added successfully.")
        # hide window again
        self.closeWindow()
    def closeWindow(self):
        # clear input and hide
        self.stringEdit.setText("")
        self.titleEdit.setText("")
        self.descEdit.setText("")
        self.priCombo.setCurrentIndex(0)
        self.dueDateEdit.setText("")
        self.dueTimeEdit.setText("")
        self.repeatCombo.setCurrentIndex(0)
        self.repeatEdit.setText("")
        self.repeatCheck.setChecked(True)
        self.tagsEdit.setText("")
        self.hide()
    def closeEvent(self, event):
        # don't actually close - window is reused
        self.closeWindow()
        event.ignore()

class list(QtGui.QMainWindow):
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

class tray(QtGui.QSystemTrayIcon):
    def __init__(self, dox):
        QtGui.QSystemTrayIcon.__init__(self)
        # components
        self.setIcon(QtGui.QIcon("check.png"))
        self.setToolTip("DoX")
        self.menu = QtGui.QMenu()
        self.addAction = self.menu.addAction("Add task...")
        self.listAction = self.menu.addAction("List tasks")
        self.menu.addSeparator()
        self.tasksAction = self.menu.addAction("Edit tasks.txt")
        self.doneAction = self.menu.addAction("Edit done.txt")
        self.menu.addSeparator()
        self.exitAction = self.menu.addAction("Exit DoX")
        self.menu.setDefaultAction(self.addAction)
        self.setContextMenu(self.menu)
        # construct other features
        self.dox = dox
        self.worker = worker(dox)
        self.addWindow = add(dox)
        self.listWindow = list(dox, self.worker)
        # connections
        self.activated.connect(self.activate)
        self.addAction.triggered.connect(self.addTask)
        self.listAction.triggered.connect(self.listTasks)
        self.tasksAction.triggered.connect(self.editTasks)
        self.doneAction.triggered.connect(self.editDone)
        self.exitAction.triggered.connect(QtGui.QApplication.quit)
        # signal listeners
        self.connect(self.worker, QtCore.SIGNAL("warning(QString, QString)"), self.warning)
        self.connect(self.addWindow, QtCore.SIGNAL("info(QString, QString)"), self.info)
        # start polling
        self.worker.start()
        # show tray icon
        self.show()
    def addTask(self):
        # bring window to front, focus on text field
        self.addWindow.show()
        self.addWindow.raise_()
        self.addWindow.stringEdit.setFocus()
    def listTasks(self):
        # bring window to front
        self.listWindow.show()
        self.listWindow.raise_()
        self.listWindow.refresh()
    def editTasks(self):
        # open a text editor with tasks.txt
        webbrowser.open(os.path.join(os.path.expanduser("~"), "DoX", "tasks.txt"))
    def editDone(self):
        # open a text editor with tasks.txt
        webbrowser.open(os.path.join(os.path.expanduser("~"), "DoX", "done.txt"))
    def info(self, title, desc):
        # information popup
        self.showMessage("DoX: " + title, desc)
    def warning(self, title, desc):
        # alert popup
        self.showMessage("DoX: " + title, desc, QtGui.QSystemTrayIcon.Warning)
    def activate(self, reason):
        # double-clicked
        if reason == 2:
            self.addTask()
        # middle-clicked
        elif reason == 4:
            self.openShell()

if __name__ == "__main__":
    # make Qt application
    app = QtGui.QApplication(sys.argv)
    # start tray icon
    foreground = tray(dox())
    # execute
    app.exec_()
