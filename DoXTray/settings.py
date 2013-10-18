# some other useful imports
import os, sys
# interface with PyQt
from PyQt4 import QtCore, QtGui

class option:
    def __init__(self, id, desc, opts=str()):
        self.id = id
        self.desc = desc
        self.opts = opts

class settings:
    def __init__(self, path=None):
        self.path = path if path else self.makePath()
        # allowed values
        self.schema = [option("taskTableRowHighlight", "Task table row highlight", ([option("none", "None"),
                                                                                     option("pri", "Priority"),
                                                                                     option("due", "Due")]))]
        # default values
        self.map = {
            "taskTableRowHighlight": "none"
        }
    def makePath(self):
        # use roaming AppData on Windows, or home directory on Mac/Linux
        return os.path.join(os.getenv("APPDATA"), "DoX Tray") if os.getenv("APPDATA") else os.path.join("~", ".DoXTray")
    def load(self):
        # no settings folder, create it
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        file = os.path.join(self.path, "settings.txt")
        # no settings file, create one
        if not os.path.exists(file):
            open(file, "w").close()
        settingsFile = open(file, "r")
        # convert schema to key list
        keys = [x.id for x in self.schema]
        # read key/value pairs from each line
        for line in settingsFile:
            key, value = [x.strip() for x in line.split("=")]
            if key in keys:
                allowed = self.schema[keys.index(key)].opts
                ok = True
                # restrict to enumerated items
                if type(allowed) == tuple:
                    ok = value in [x.id for x in allowed[0]]
                # parse as integer
                elif type(allowed) == int:
                    try:
                        value = int(value)
                    except ValueError:
                        ok = False
                if ok:
                    # valid value, add to map
                    self.map[key] = value
        settingsFile.close()
    def save(self):
        # no settings folder, create it
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        file = os.path.join(self.path, "settings.txt")
        # write key value pairs to file
        settingsFile = open(file, "w")
        for key in self.map:
            settingsFile.write(key + " = " + str(self.map[key]) + "\n")
        settingsFile.close()
    def get(self, key):
        # shorthand to get a value
        return self.map[key]
    def set(self, key, value):
        # shorthand to set a value
        self.map[key] = value

class settingsWindow(QtGui.QDialog):
    def __init__(self, settings):
        QtGui.QDialog.__init__(self)
        self.settings = settings
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.setWindowTitle("DoX: Settings")
        self.setWindowIcon(QtGui.QIcon("check.png"))
        self.resize(200, 71)
        self.setGeometry(QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter, self.size(),
                                                  QtGui.QDesktopWidget().availableGeometry()))
        # main widget
        self.setLayout(self.build())
    def build(self):
        # controls
        self.settingIds = []
        settingLabels = []
        self.settingControls = []
        for setting in self.settings.schema:
            self.settingIds.append(setting.id)
            settingLabels.append(QtGui.QLabel(setting.desc))
            value = self.settings.get(setting.id)
            # create a dropdown of options
            if type(setting.opts) == list:
                control = QtGui.QComboBox()
                control.addItems([x.desc for x in setting.opts])
                control.setCurrentIndex([x.id for x in setting.opts].index(value))
            # numeric spinbox
            elif type(setting.opts) == int:
                control = QtGui.QSpinBox()
                control.setValue(value)
            # plain text box
            else:
                control = QtGui.QLineEdit()
                control.setText(value)
            self.settingControls.append(control)
        self.saveButton = QtGui.QPushButton("Save")
        self.cancelButton = QtGui.QPushButton("Cancel")
        # layouts
        bottomLayout = QtGui.QHBoxLayout()
        bottomLayout.addWidget(self.saveButton)
        bottomLayout.addWidget(self.cancelButton)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        # make a label/control grid
        controlLayout = QtGui.QGridLayout()
        for x in range(len(self.settingIds)):
            controlLayout.addWidget(settingLabels[x], x, 0)
            controlLayout.addWidget(self.settingControls[x], x, 1)
        self.mainLayout.addLayout(controlLayout)
        self.mainLayout.addLayout(bottomLayout)
        # connections
        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.close)
        # return new layout
        return self.mainLayout
    def save(self):
        for x in range(len(self.settingIds)):
            # read back each setting
            setting = self.settings.schema[x]
            control = self.settingControls[x]
            if type(setting.opts) == list:
                value = [x.id for x in setting.opts][control.currentIndex()]
            elif type(setting.opts) == int:
                value = control.value()
            else:
                value = control.text()
            self.settings.set(self.settingIds[x], value)
        # commit changes
        self.settings.save()
        self.close()
        # trigger refresh for all windows
        self.emit(QtCore.SIGNAL("refresh()"))
    def closeEvent(self, event):
        # don't actually close - window is reused
        self.hide()
        event.ignore()