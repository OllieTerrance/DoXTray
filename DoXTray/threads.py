# some other useful imports
import datetime, time
# PyQt threading
from PyQt4 import QtCore

class fileMonitor(QtCore.QThread):
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
    def run(self):
        while True:
            self.checkFile()
            # sleep for a bit
            time.sleep(5)
    def checkFile(self):
        # tasks list has been modified since last check
        if self.dox.tasksFileLastMod() > self.fileLastMod:
            # reload tasks from file
            self.dox.loadTasks()
            # update last mod. time
            self.fileLastMod = self.dox.tasksFileLastMod()
            # trigger refresh for list and edit windows
            self.emit(QtCore.SIGNAL("refresh()"))

class dueMonitor(QtCore.QThread):
    def __init__(self, dox):
        QtCore.QThread.__init__(self)
        # connect to API
        self.dox = dox
        # empty list of past notifications
        self.notified = []
    def run(self):
        while True:
            now = datetime.datetime.now()
            today = datetime.datetime.combine(now.date(), datetime.time())
            noTasks = True
            # remove tasks from notified that don't exist
            self.notified = [x for x in self.notified if x[0] in self.dox.tasks]
            # loop all tasks
            for taskObj in self.dox.tasks:
                # if task is due now
                if taskObj.due and ((taskObj.due[1] and taskObj.due[0] < now) or (not taskObj.due[1] and taskObj.due[0] <= today)):
                    # check it hasn't been notified recently
                    ok = True
                    for notify in self.notified:
                        # compare to see if notified about before
                        if notify[0] == taskObj:
                            # if notified about in the last hour
                            if notify[1] + datetime.timedelta(hours=1) > now:
                                ok = False
                            else:
                                # remove previous record as new one will be added
                                self.notified.remove(notify)
                            break
                    if ok:
                        noTasks = False
                        # popup alert
                        self.emit(QtCore.SIGNAL("warning(QString, QString)"), taskObj.title, (taskObj.desc if taskObj.desc else "Due now!"))
                        # add to known notified list
                        self.notified.append((taskObj, now))
                        # only do one for now
                        break
            # if nothing to notify about, sleep for a while
            time.sleep(60 if noTasks else 10)
