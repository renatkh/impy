# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DuplicateDialog.ui'
#
# Created: Wed Apr 25 23:31:50 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(183, 87)
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Duplicate", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.current = QtGui.QRadioButton(Dialog)
        self.current.setText(QtGui.QApplication.translate("Dialog", "Current", None, QtGui.QApplication.UnicodeUTF8))
        self.current.setChecked(True)
        self.current.setAutoExclusive(True)
        self.current.setObjectName(_fromUtf8("current"))
        self.verticalLayout.addWidget(self.current)
        self.stackLayout = QtGui.QHBoxLayout()
        self.stackLayout.setObjectName(_fromUtf8("stackLayout"))
        self.stack = QtGui.QRadioButton(Dialog)
        self.stack.setText(QtGui.QApplication.translate("Dialog", "Stack", None, QtGui.QApplication.UnicodeUTF8))
        self.stack.setObjectName(_fromUtf8("stack"))
        self.stackLayout.addWidget(self.stack)
        self.stackRange = QtGui.QLineEdit(Dialog)
        self.stackRange.setObjectName(_fromUtf8("stackRange"))
        self.stackLayout.addWidget(self.stackRange)
        self.verticalLayout.addLayout(self.stackLayout)
        self.buttons = QtGui.QDialogButtonBox(Dialog)
        self.buttons.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttons.setObjectName(_fromUtf8("buttons"))
        self.verticalLayout.addWidget(self.buttons)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttons, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.close)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass

