# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CadInput
                                 A QGIS plugin
 Provides CAD-like input globally : digitize features with precise numerical input for the angle, the distance, and easily make widCuctions lines
                              -------------------
        begin                : 2014-01-15
        copyright            : (C) 2014 by Olivier Dalang
        email                : olivier.dalang@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import math
import ast
import operator as op

class CadWidget(QWidget):
    """
    This is CadInput's main GUI widget. It displays the edit fields for entering numerical coordinates.
    """

    valueEdited = pyqtSignal()

    def __init__(self, iface):
        QWidget.__init__(self)

        self.iface = iface

        # We want to get focus so KeyPressEvents can be processed (useful for internal shortcuts)
        self.setFocusPolicy(Qt.ClickFocus)

        gridLayout = QGridLayout() 


        # Create the widgets

        ## General

        self.widC = QToolButton()
        self.widC.setText("construction")
        self.widC.setCheckable(True)

        ## Angular

        self.relD = QToolButton()
        self.relD.setText("D")
        self.relD.setCheckable(True)
        self.relD.setChecked(True)
        self.relD.setEnabled(False)

        self.widD = QLineEditWithShortcut(self)
        self.lockD = QToolButton()
        self.lockD.setText("L")
        self.lockD.setCheckable(True)

        self.relA = QToolButton()
        self.relA.setText("D")
        self.relA.setCheckable(True)
        self.relA.setChecked(True)

        self.widA = QLineEditWithShortcut(self)
        self.lockA = QToolButton()
        self.lockA.setText("L")
        self.lockA.setCheckable(True)

        ## Cartesian

        self.relX = QToolButton()
        self.relX.setText("D")
        self.relX.setCheckable(True)
        self.relX.setChecked(True)

        self.widX = QLineEditWithShortcut(self)
        self.lockX = QToolButton()
        self.lockX.setText("L")
        self.lockX.setCheckable(True)

        self.relY = QToolButton()
        self.relY.setText("D")
        self.relY.setCheckable(True)
        self.relY.setChecked(True)

        self.widY = QLineEditWithShortcut(self)
        self.lockY = QToolButton()
        self.lockY.setText("L")
        self.lockY.setCheckable(True)



        # Connect the signals

        #when return is pressed, we want to lock the value
        self.widD.returnPressed.connect(lambda: self.validateField(self.widD, self.lockD))
        self.widA.returnPressed.connect(lambda: self.validateField(self.widA, self.lockA))
        self.widX.returnPressed.connect(lambda: self.validateField(self.widX, self.lockX))
        self.widY.returnPressed.connect(lambda: self.validateField(self.widY, self.lockY))

        #when an angular field is locked, we want to unlock the cartesian fields, and the other way too
        def disableIfEnabled(state, target):
            if state: target.setChecked(False)

        self.lockY.toggled.connect(lambda state: disableIfEnabled(state,self.lockD))
        self.lockY.toggled.connect(lambda state: disableIfEnabled(state,self.lockA))
        self.lockX.toggled.connect(lambda state: disableIfEnabled(state,self.lockD))
        self.lockX.toggled.connect(lambda state: disableIfEnabled(state,self.lockA))

        self.lockD.toggled.connect(lambda state: disableIfEnabled(state,self.lockX))
        self.lockD.toggled.connect(lambda state: disableIfEnabled(state,self.lockY))
        self.lockA.toggled.connect(lambda state: disableIfEnabled(state,self.lockX))
        self.lockA.toggled.connect(lambda state: disableIfEnabled(state,self.lockY))

        #when a field is edited by the user, we fire the valueEdited signal to be able notify the ghostwidget it must update 
        self.widD.textEdited.connect(self.valueEdited)
        self.widA.textEdited.connect(self.valueEdited)
        self.widX.textEdited.connect(self.valueEdited)
        self.widY.textEdited.connect(self.valueEdited)
        self.lockD.toggled.connect(self.valueEdited)
        self.lockA.toggled.connect(self.valueEdited)
        self.lockX.toggled.connect(self.valueEdited)
        self.lockA.toggled.connect(self.valueEdited)

        # Layout the widgets

        r=0
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.widC)
        gridLayout.addLayout(sublayout,r,0,1,4 )

        r+=1
        gridLayout.addWidget(self.relD,r,0 )
        gridLayout.addWidget(QLabel("length"),r,1 )
        gridLayout.addWidget(self.widD,r,2 )
        gridLayout.addWidget(self.lockD,r,3 )

        r+=1
        gridLayout.addWidget(self.relA,r,0 )
        gridLayout.addWidget(QLabel("angle"),r,1 )
        gridLayout.addWidget(self.widA,r,2 )
        gridLayout.addWidget(self.lockA,r,3 )

        r+=1
        gridLayout.addWidget(self.relX,r,0 )
        gridLayout.addWidget(QLabel("x"),r,1 )
        gridLayout.addWidget(self.widX,r,2 )
        gridLayout.addWidget(self.lockX,r,3 )

        r+=1
        gridLayout.addWidget(self.relY,r,0 )
        gridLayout.addWidget(QLabel("y"),r,1 )
        gridLayout.addWidget(self.widY,r,2 )
        gridLayout.addWidget(self.lockY,r,3 )

        r+=1
        self.click = QPushButton()
        self.click.setText("click")
        gridLayout.addWidget(self.click,r,0,1,4 )

        self.setLayout(gridLayout)

    # Basic properties
    @property
    def x(self):return floatOrZero(self.widX.text())
    @x.setter
    def x(self, value): self.widX.setText(str(value))

    @property
    def y(self):return floatOrZero(self.widY.text())
    @y.setter
    def y(self, value): self.widY.setText(str(value))

    @property
    def d(self):return floatOrZero(self.widD.text())
    @d.setter
    def d(self, value): self.widD.setText(str(value))

    @property
    def a(self):return floatOrZero(self.widA.text())
    @a.setter
    def a(self, value): self.widA.setText(str(value))

    #Lock properties
    @property
    def lx(self): return self.lockX.isChecked()
    @lx.setter
    def lx(self, value): self.lockX.setChecked(value)

    @property
    def ly(self): return self.lockY.isChecked()
    @ly.setter
    def ly(self, value): self.lockY.setChecked(value)

    @property
    def la(self): return self.lockA.isChecked()
    @la.setter
    def la(self, value): self.lockA.setChecked(value)

    @property
    def ld(self): return self.lockD.isChecked()
    @ld.setter
    def ld(self, value): self.lockD.setChecked(value)

    #Relative properties
    @property
    def rx(self): return self.relX.isChecked()
    @rx.setter
    def rx(self, value): self.relX.setChecked(value)

    @property
    def ry(self): return self.relY.isChecked()
    @ry.setter
    def ry(self, value): self.relY.setChecked(value)

    @property
    def ra(self): return self.relA.isChecked()
    @ra.setter
    def ra(self, value): self.relA.setChecked(value)

    @property
    def rd(self): return True
    @rd.setter
    def rd(self, value): raise Exception

    #Misc properties
    @property
    def c(self): return self.widC.isChecked()
    @c.setter
    def c(self, value): self.widC.setChecked(value)


    def keyPressEvent(self, event):
        """
        This implements the internal shortcuts when the focus is in the widget (e.g. on a QPushButton)
        """

        if event.key() == Qt.Key_X:
            if event.modifiers() == Qt.ShiftModifier:
                self.lockX.toggle()
            else:
                self.widX.setFocus()
                self.widX.selectAll()
        elif event.key() == Qt.Key_Y:
            if event.modifiers() == Qt.ShiftModifier:
                self.lockY.toggle()
            else:
                self.widY.setFocus()
                self.widY.selectAll()
        elif event.key() == Qt.Key_A:
            if event.modifiers() == Qt.ShiftModifier:
                self.lockA.toggle()
            else:
                self.widA.setFocus()
                self.widA.selectAll()
        elif event.key() == Qt.Key_D:
            if event.modifiers() == Qt.ShiftModifier:
                self.lockD.toggle()
            else:
                self.widD.setFocus()
                self.widD.selectAll()
        elif event.key() == Qt.Key_C:
            self.widC.toggle()
        else:
            QWidget.keyPressEvent(self,event)

    def validateField(self, field, lock):
        s = field.text()
        if s == "":
            lock.setChecked(False)
        else:
            v = Evaluator.eval_expr(field.text())
            if v is None:
                lock.setChecked(False)
                field.setText( "" )
            else:
                lock.setChecked(True)
                field.setText( str( v ) )

def floatOrZero(value):
    """
    Since float("") throws an error, we need to use this
    """
    try: return float(value)
    except: return 0.0

class QLineEditWithShortcut(QLineEdit):
    """
    This class allows for internal shortcuts inside QLineEdit when they are being edited.
    """

    def __init__(self, cadwidget):
        QLineEdit.__init__(self, "0")
        self.cadwidget = cadwidget

    def keyPressEvent(self, event):
        self.textEdited.emit(self.text())
        if event.key() == Qt.Key_X:
            if event.modifiers() == Qt.ShiftModifier:
                self.cadwidget.lockX.toggle()
            else:
                self.cadwidget.widX.setFocus()
                self.cadwidget.widX.selectAll()
        elif event.key() == Qt.Key_Y:
            if event.modifiers() == Qt.ShiftModifier:
                self.cadwidget.lockY.toggle()
            else:
                self.cadwidget.widY.setFocus()
                self.cadwidget.widY.selectAll()
        elif event.key() == Qt.Key_A:
            if event.modifiers() == Qt.ShiftModifier:
                self.cadwidget.lockA.toggle()
            else:
                self.cadwidget.widA.setFocus()
                self.cadwidget.widA.selectAll()
        elif event.key() == Qt.Key_D:
            if event.modifiers() == Qt.ShiftModifier:
                self.cadwidget.lockD.toggle()
            else:
                self.cadwidget.widD.setFocus()
                self.cadwidget.widD.selectAll()
        elif event.key() == Qt.Key_C:
            self.cadwidget.widC.toggle()
        else:
            QLineEdit.keyPressEvent(self,event)


class Evaluator():
    """
    Evaluates strings, code from http://stackoverflow.com/a/9558001/2615469
    """

    # supported operators
    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor}

    @staticmethod
    def eval_expr(expr):
        return Evaluator.eval_(ast.parse(expr).body[0].value) # Module(body=[Expr(value=...)])

    @staticmethod
    def eval_(node):
        if isinstance(node, ast.Num): # <number>
            return node.n
        elif isinstance(node, ast.operator): # <operator>
            return Evaluator.operators[type(node)]
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return Evaluator.eval_(node.op)(Evaluator.eval_(node.left), Evaluator.eval_(node.right))
        else:
            return None
            #raise TypeError(node)
