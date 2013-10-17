# some other useful imports
import os, sys, webbrowser
# main class import
from DoX.core import *
# window class imports
from add import *
from lists import *
from settings import *
# threading class imports
from threads import *
# interface with PyQt
from PyQt4 import QtCore, QtGui

class aboutWindow(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.setWindowTitle("DoX: About")
        self.setWindowIcon(QtGui.QIcon("check.png"))
        self.resize(222, 132)
        self.setGeometry(QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter, self.size(),
                                                  QtGui.QDesktopWidget().availableGeometry()))
        # main widget
        self.setLayout(self.build())
    def build(self):
        # controls
        titleLabel = QtGui.QLabel("<span style=\"font-size: 12pt; font-weight: bold;\">DoX</span>&nbsp; dev")
        titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        descLabel = QtGui.QLabel("This is DoX, as in <b>do &lt;X&gt;</b>, where <b>X</b> is a<br/>task, but also pronounceable like \"docks\".")
        descLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.okButton = QtGui.QPushButton("Ok")
        self.aboutButton = QtGui.QPushButton("About")
        self.authorButton = QtGui.QPushButton("Author")
        self.githubButton = QtGui.QPushButton("GitHub")
        # layouts
        bottomLayout1 = QtGui.QHBoxLayout()
        bottomLayout1.addWidget(self.okButton)
        bottomLayout1.addWidget(self.aboutButton)
        bottomLayout2 = QtGui.QHBoxLayout()
        bottomLayout2.addWidget(self.authorButton)
        bottomLayout2.addWidget(self.githubButton)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.mainLayout.addWidget(titleLabel)
        self.mainLayout.addWidget(descLabel)
        self.mainLayout.addLayout(bottomLayout1)
        self.mainLayout.addLayout(bottomLayout2)
        # connections
        self.okButton.clicked.connect(self.close)
        self.aboutButton.clicked.connect(self.about)
        self.authorButton.clicked.connect(self.author)
        self.githubButton.clicked.connect(self.github)
        # return new layout
        return self.mainLayout
    def about(self):
        webbrowser.open("http://dox.uk.to/about.html")
        self.close()
    def author(self):
        webbrowser.open("http://terrance.uk.to")
        self.close()
    def github(self):
        webbrowser.open("https://github.com/OllieTerrance/DoXTray")
        self.close()
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
        # core
        self.dox = dox
        self.settings = settings()
        self.settings.load()
        # threads
        self.fileMonitor = fileMonitor(self.dox)
        self.dueMonitor = dueMonitor(self.dox)
        # windows
        self.aboutWindow = aboutWindow()
        self.addWindow = addWindow(self.dox)
        self.listsWindow = listsWindow(self.dox, self.fileMonitor)
        self.settingsWindow = settingsWindow(self.settings)
        # connections
        self.activated.connect(self.activate)
        # signal listeners
        self.connect(self.fileMonitor, QtCore.SIGNAL("refresh()"), self.listsWindow.refresh)
        self.connect(self.fileMonitor, QtCore.SIGNAL("refresh()"), self.makeMenu)
        self.connect(self.dueMonitor, QtCore.SIGNAL("warning(QString, QString)"), self.warning)
        self.connect(self.addWindow, QtCore.SIGNAL("info(QString, QString)"), self.info)
        self.connect(self, QtCore.SIGNAL("refresh()"), self.listsWindow.refresh)
        self.connect(self.addWindow, QtCore.SIGNAL("refresh()"), self.listsWindow.refresh)
        self.connect(self.listsWindow, QtCore.SIGNAL("addTask()"), self.addTask)
        self.connect(self.listsWindow, QtCore.SIGNAL("listsSaved()"), self.makeMenu)
        self.connect(self.listsWindow, QtCore.SIGNAL("listsSaved()"), self.fileMonitor.checkFile)
        # start polling
        self.fileMonitor.start()
        self.dueMonitor.start()
        # context menu
        self.makeMenu()
        # show tray icon
        self.show()
    def makeMenu(self):
        self.mainMenu = QtGui.QMenu()
        listsAction = self.mainMenu.addAction("&List tasks")
        listsAction.triggered.connect(self.listTasks)
        addAction = self.mainMenu.addAction("&Add task...")
        addAction.triggered.connect(self.addTask)
        self.mainMenu.addSeparator()
        # submenu to quickly complete a task
        if self.dox.getCount():
            self.markDoneMenu = self.mainMenu.addMenu("Mark &done")
            tasks = self.dox.getAllTasks()
            for taskObj in tasks:
                pos = self.dox.idToPos(taskObj.id)
                markAction = self.markDoneMenu.addAction("{}{}. {}".format("&" if pos <= 9 else "", pos, taskObj.title.replace("&", "&&")))
                markAction.setData(pos)
                markAction.triggered.connect(self.markDone)
        # submenu to quickly undo a task
        if self.dox.getCount(False):
            self.markUndoMenu = self.mainMenu.addMenu("&Undo task")
            tasks = self.dox.getAllTasks(False)
            for taskObj in tasks:
                pos = self.dox.idToPos(taskObj.id, False)
                markAction = self.markUndoMenu.addAction("{}{}. {}".format("&" if pos <= 9 else "", pos, taskObj.title.replace("&", "&&")))
                markAction.setData(pos)
                markAction.triggered.connect(self.markUndo)
        self.mainMenu.addSeparator()
        settingsAction = self.mainMenu.addAction("Edit &settings")
        settingsAction.triggered.connect(self.editSettings)
        tasksAction = self.mainMenu.addAction("&Edit tasks.txt")
        tasksAction.triggered.connect(self.editTasks)
        doneAction = self.mainMenu.addAction("Edi&t done.txt")
        doneAction.triggered.connect(self.editDone)
        self.mainMenu.addSeparator()
        aboutAction = self.mainMenu.addAction("A&bout DoX...")
        aboutAction.triggered.connect(self.about)
        exitAction = self.mainMenu.addAction("E&xit")
        exitAction.triggered.connect(self.exit)
        # default to listing tasks
        self.mainMenu.setDefaultAction(listsAction)
        # assign the menu
        self.setContextMenu(self.mainMenu)
    def addTask(self):
        # bring window to front, focus on text field
        self.addWindow.show()
        self.addWindow.raise_()
        self.addWindow.stringEdit.setFocus()
    def listTasks(self):
        # bring window to front
        self.listsWindow.show()
        self.listsWindow.raise_()
        # set initial split position
        if not self.listsWindow.splitMoved:
            self.listsWindow.splitWidget.moveSplitter(760, 1)
            self.listsWindow.splitMoved = True
        self.listsWindow.refresh()
    def markDone(self):
        # fetch task associated with action
        pos = self.sender().data()
        # mark as done
        self.dox.doneNthTask(pos)
        # resave and refresh
        self.saveAndRefresh()
    def markUndo(self):
        # fetch task associated with action
        pos = self.sender().data()
        # mark as done
        self.dox.undoNthTask(pos)
        # resave and refresh
        self.saveAndRefresh()
    def saveAndRefresh(self):
        # save tasks
        self.dox.saveTasks()
        # update lists window if open
        self.emit(QtCore.SIGNAL("refresh()"))
        # update context menu
        self.makeMenu()
    def editSettings(self):
        # bring window to front
        self.settingsWindow.show()
        self.settingsWindow.raise_()
        self.settingsWindow.saveButton.setFocus()
    def editTasks(self):
        # open a text editor with tasks.txt
        webbrowser.open(os.path.join(os.path.expanduser("~"), "DoX", "tasks.txt"))
    def editDone(self):
        # open a text editor with tasks.txt
        webbrowser.open(os.path.join(os.path.expanduser("~"), "DoX", "done.txt"))
    def about(self):
        # bring window to front
        self.aboutWindow.show()
        self.aboutWindow.raise_()
        self.aboutWindow.okButton.setFocus()
    def info(self, title, desc):
        # information popup
        self.showMessage("DoX: " + title, desc)
    def warning(self, title, desc):
        # alert popup
        self.showMessage("DoX: " + title, desc, QtGui.QSystemTrayIcon.Warning)
    def activate(self, reason):
        # double-clicked
        if reason == 2:
            self.listTasks()
        # middle-clicked
        elif reason == 4:
            self.addTask()
    def exit(self):
        self.settings.save()
        QtGui.QApplication.quit()

if __name__ == "__main__":
    # make Qt application
    app = QtGui.QApplication(sys.argv)
    # start tray icon
    foreground = tray(dox())
    # execute
    app.exec_()
