# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dock.ui'
#
# Created: Mon Feb 03 20:11:50 2014
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_CadInputDock(object):
    def setupUi(self, CadInputDock):
        CadInputDock.setObjectName(_fromUtf8("CadInputDock"))
        CadInputDock.resize(176, 221)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.widEnab = QtGui.QToolButton(self.dockWidgetContents)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadinput/resources/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.widEnab.setIcon(icon)
        self.widEnab.setIconSize(QtCore.QSize(24, 24))
        self.widEnab.setObjectName(_fromUtf8("widEnab"))
        self.horizontalLayout.addWidget(self.widEnab)
        self.widC = QtGui.QToolButton(self.dockWidgetContents)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadinput/resources/construction.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.widC.setIcon(icon1)
        self.widC.setIconSize(QtCore.QSize(24, 24))
        self.widC.setCheckable(True)
        self.widC.setObjectName(_fromUtf8("widC"))
        self.horizontalLayout.addWidget(self.widC)
        self.widPer = QtGui.QToolButton(self.dockWidgetContents)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadinput/resources/perpendicular.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.widPer.setIcon(icon2)
        self.widPer.setIconSize(QtCore.QSize(24, 24))
        self.widPer.setCheckable(True)
        self.widPer.setObjectName(_fromUtf8("widPer"))
        self.horizontalLayout.addWidget(self.widPer)
        self.widPar = QtGui.QToolButton(self.dockWidgetContents)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadinput/resources/parallel.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.widPar.setIcon(icon3)
        self.widPar.setIconSize(QtCore.QSize(24, 24))
        self.widPar.setCheckable(True)
        self.widPar.setObjectName(_fromUtf8("widPar"))
        self.horizontalLayout.addWidget(self.widPar)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.relD = QtGui.QToolButton(self.dockWidgetContents)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadinput/resources/delta.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.relD.setIcon(icon4)
        self.relD.setCheckable(True)
        self.relD.setObjectName(_fromUtf8("relD"))
        self.gridLayout_2.addWidget(self.relD, 0, 0, 1, 1)
        self.relA = QtGui.QToolButton(self.dockWidgetContents)
        self.relA.setIcon(icon4)
        self.relA.setCheckable(True)
        self.relA.setObjectName(_fromUtf8("relA"))
        self.gridLayout_2.addWidget(self.relA, 1, 0, 1, 1)
        self.relY = QtGui.QToolButton(self.dockWidgetContents)
        self.relY.setIcon(icon4)
        self.relY.setCheckable(True)
        self.relY.setObjectName(_fromUtf8("relY"))
        self.gridLayout_2.addWidget(self.relY, 3, 0, 1, 1)
        self.relX = QtGui.QToolButton(self.dockWidgetContents)
        self.relX.setIcon(icon4)
        self.relX.setCheckable(True)
        self.relX.setObjectName(_fromUtf8("relX"))
        self.gridLayout_2.addWidget(self.relX, 2, 0, 1, 1)
        self.lockD = QtGui.QToolButton(self.dockWidgetContents)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadinput/resources/lock.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.lockD.setIcon(icon5)
        self.lockD.setCheckable(True)
        self.lockD.setObjectName(_fromUtf8("lockD"))
        self.gridLayout_2.addWidget(self.lockD, 0, 3, 1, 1)
        self.lockA = QtGui.QToolButton(self.dockWidgetContents)
        self.lockA.setIcon(icon5)
        self.lockA.setCheckable(True)
        self.lockA.setObjectName(_fromUtf8("lockA"))
        self.gridLayout_2.addWidget(self.lockA, 1, 3, 1, 1)
        self.lockX = QtGui.QToolButton(self.dockWidgetContents)
        self.lockX.setIcon(icon5)
        self.lockX.setCheckable(True)
        self.lockX.setObjectName(_fromUtf8("lockX"))
        self.gridLayout_2.addWidget(self.lockX, 2, 3, 1, 1)
        self.lockY = QtGui.QToolButton(self.dockWidgetContents)
        self.lockY.setIcon(icon5)
        self.lockY.setCheckable(True)
        self.lockY.setObjectName(_fromUtf8("lockY"))
        self.gridLayout_2.addWidget(self.lockY, 3, 3, 1, 1)
        self.label_2 = QtGui.QLabel(self.dockWidgetContents)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.dockWidgetContents)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.dockWidgetContents)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 3, 1, 1, 1)
        self.widA = QtGui.QLineEdit(self.dockWidgetContents)
        self.widA.setObjectName(_fromUtf8("widA"))
        self.gridLayout_2.addWidget(self.widA, 1, 2, 1, 1)
        self.widX = QtGui.QLineEdit(self.dockWidgetContents)
        self.widX.setObjectName(_fromUtf8("widX"))
        self.gridLayout_2.addWidget(self.widX, 2, 2, 1, 1)
        self.widY = QtGui.QLineEdit(self.dockWidgetContents)
        self.widY.setObjectName(_fromUtf8("widY"))
        self.gridLayout_2.addWidget(self.widY, 3, 2, 1, 1)
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 1, 1, 1)
        self.widD = QtGui.QLineEdit(self.dockWidgetContents)
        self.widD.setObjectName(_fromUtf8("widD"))
        self.gridLayout_2.addWidget(self.widD, 0, 2, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)
        CadInputDock.setWidget(self.dockWidgetContents)
        self.enableAction = QtGui.QAction(CadInputDock)
        self.enableAction.setCheckable(True)
        self.enableAction.setIcon(icon)
        self.enableAction.setObjectName(_fromUtf8("enableAction"))

        self.retranslateUi(CadInputDock)
        QtCore.QMetaObject.connectSlotsByName(CadInputDock)

    def retranslateUi(self, CadInputDock):
        CadInputDock.setWindowTitle(_translate("CadInputDock", "CadInput", None))
        self.widEnab.setText(_translate("CadInputDock", "...", None))
        self.widC.setText(_translate("CadInputDock", "...", None))
        self.widPer.setText(_translate("CadInputDock", "...", None))
        self.widPar.setText(_translate("CadInputDock", "...", None))
        self.relD.setText(_translate("CadInputDock", "...", None))
        self.relA.setText(_translate("CadInputDock", "...", None))
        self.relY.setText(_translate("CadInputDock", "...", None))
        self.relX.setText(_translate("CadInputDock", "...", None))
        self.lockD.setText(_translate("CadInputDock", "...", None))
        self.lockA.setText(_translate("CadInputDock", "...", None))
        self.lockX.setText(_translate("CadInputDock", "...", None))
        self.lockY.setText(_translate("CadInputDock", "...", None))
        self.label_2.setText(_translate("CadInputDock", "a", None))
        self.label_3.setText(_translate("CadInputDock", "x", None))
        self.label_4.setText(_translate("CadInputDock", "y", None))
        self.label.setText(_translate("CadInputDock", "d", None))
        self.enableAction.setText(_translate("CadInputDock", "Enable", None))

import resources_rc
