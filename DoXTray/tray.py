# some other useful imports
import os, sys, webbrowser
# add DoX core to path
sys.path.append("dox")
# main class import
from dox import *
# window class imports
from add import *
from lists import *
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

class tray(QtGui.QSystemTrayIcon):
    def __init__(self, dox):
        QtGui.QSystemTrayIcon.__init__(self)
        # components
        self.setIcon(QtGui.QIcon("check.png"))
        self.setToolTip("DoX")
        self.menu = QtGui.QMenu()
        self.addAction = self.menu.addAction("Add task...")
        self.listsAction = self.menu.addAction("List tasks")
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
        self.listsWindow = lists(dox, self.worker)
        # connections
        self.activated.connect(self.activate)
        self.addAction.triggered.connect(self.addTask)
        self.listsAction.triggered.connect(self.listTasks)
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
        self.listsWindow.show()
        self.listsWindow.raise_()
        self.listsWindow.refresh()
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
