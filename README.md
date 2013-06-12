Introduction
------------

DoX is a feature-packed to-do list application in Python.  DoXTray allows you to add, manage and complete your tasks from a graphical interface.

Tasks to do are stored in tasks.txt, and completed tasks in done.txt, both in the DoX folder in your home directory.

The system tray icon provides a menu with access to a task list and new task dialog.  It also shows reminders when tasks become due.


Prerequisites
-------------

This program relies on the DoX API, which is not included in this package.  You must [download](http://github.com/OllieTerrance/DoX) and install it separately, then provide a copy of the files (through symlink or otherwise) in a `dox` folder within the `DoXTray` folder.
