# some other useful imports
import datetime, shlex, sys, time
# utility class import
from DoX.util import *
# interface with PyQt
from PyQt4 import QtCore, QtGui

class addWindow(QtGui.QMainWindow):
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
        self.priCombo.addItems(["Low (0)", "Medium (1)", "High (2)", "Critical (3)"])
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
        self.tagsEdit.textChanged.connect(self.tagsEditChanged)
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
        # set due to today if enabling repeat and no due date
        if index and not self.dueDateEdit.text():
            self.dueDateEdit.setText("today")
            self.dueEditFinished(True)
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
    def tagsEditChanged(self):
        try:
            # attempt to split tags
            shlex.split(str(self.tagsEdit.text()))
        except ValueError:
            # highlight error
            self.tagsEdit.setStyleSheet("background-color: #F88;")
            # attempt to guess fault with string
            string = self.tagsEdit.text()
            if string.count("\"") % 2 == 1:
                self.tagsEdit.setToolTip("Unbalanced double quote?")
            elif string.count("'") % 2 == 1:
                self.tagsEdit.setToolTip("Unbalanced single quote?")
            elif string.count("\\") % 2 == 1:
                self.tagsEdit.setToolTip("Unbalanced backslash?")
            # don't process any further
            return
        # clear error highlight if previously set
        self.tagsEdit.setStyleSheet("")
        self.tagsEdit.setToolTip("")
        # remember current input as good
        self.lastValidTags = self.tagsEdit.text()
        # update string field
        self.fieldsUp()
    def tagsEditFinished(self):
        try:
            # attempt to split tags
            shlex.split(str(self.tagsEdit.text()))
        except ValueError:
            # can't parse, reset to last known valid value
            self.tagsEdit.setText(self.lastValidTags)
            self.tagsEdit.setFocus()
            # update string field
            self.fieldsUp()
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
        self.stringEdit.setText(formatArgs(None, title, desc, pri, due, repeat, tags))
    def fieldsDown(self):
        try:
            # parse with shlex
            args = shlex.split(str(self.stringEdit.text()))
            # clear error highlight if previously set
            self.stringEdit.setStyleSheet("")
            self.stringEdit.setToolTip("")
        except:
            # can't parse, refocus until complete
            self.stringEdit.setFocus()
            # highlight error
            self.stringEdit.setStyleSheet("background-color: #F88;")
            # attempt to guess fault with string
            string = self.stringEdit.text()
            if string.count("\"") % 2 == 1:
                self.stringEdit.setToolTip("Unbalanced double quote?")
            elif string.count("'") % 2 == 1:
                self.stringEdit.setToolTip("Unbalanced single quote?")
            elif string.count("\\") % 2 == 1:
                self.stringEdit.setToolTip("Unbalanced backslash?")
            # don't process any further
            return
        # process arguments with standard parser
        id, title, desc, pri, due, repeat, tags = parseArgs(args)
        # set basic fields
        self.titleEdit.setText(title)
        self.descEdit.setText(desc)
        self.priCombo.setCurrentIndex(pri)
        self.dueDateEdit.setText("")
        self.dueTimeEdit.setText("")
        if due:
            # set full date due
            self.dueDateEdit.setText(due[0].strftime("%d/%m/%Y"))
            self.dueTimeEdit.setText(due[0].strftime("%H:%M:%S" if due[1] else ""))
        self.repeatCombo.setCurrentIndex(0)
        self.repeatEdit.setText("")
        self.repeatEdit.setEnabled(False)
        if repeat:
            # use daily alias
            if repeat[0] == 1:
                self.repeatCombo.setCurrentIndex(1)
            # use weekly alias
            elif repeat[0] == 7:
                self.repeatCombo.setCurrentIndex(2)
            # use fortnightly alias
            elif repeat[0] == 14:
                self.repeatCombo.setCurrentIndex(3)
            # custom, set edit field enabled
            else:
                self.repeatCombo.setCurrentIndex(4)
                self.repeatEdit.setEnabled(True)
            # from done unless set otherwise
            self.repeatCheck.setChecked(True)
            if repeat[1]:
                self.repeatCheck.setChecked(False)
        # remove hashes and re-quote
        self.tagsEdit.setText(" ".join([quote(x) for x in tags]))
    def addTask(self):
        # fetch string and parse
        string = str(self.stringEdit.text())
        args = parseArgs(shlex.split(string))
        if len(args):
            # expand args tuple when passed to addTask, skipping ID
            self.dox.addTask(*args[1:])
            # resave
            self.dox.saveTasks()
            # trigger refresh for list window
            self.emit(QtCore.SIGNAL("refresh()"))
            # show notification
            self.emit(QtCore.SIGNAL("info(QString, QString)"), args[1], "Task added successfully.")
        # hide window again
        self.closeWindow()
    def closeWindow(self):
        # clear input and hide
        self.titleEdit.setText("")
        self.descEdit.setText("")
        self.priCombo.setCurrentIndex(0)
        self.dueDateEdit.setText("")
        self.dueTimeEdit.setText("")
        self.repeatCombo.setCurrentIndex(0)
        self.repeatEdit.setText("")
        self.repeatCheck.setChecked(True)
        self.tagsEdit.setText("")
        self.stringEdit.setText("")
        self.hide()
    def closeEvent(self, event):
        # don't actually close - window is reused
        self.closeWindow()
        event.ignore()
