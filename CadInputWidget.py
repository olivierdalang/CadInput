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
import ast
import operator as op

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_dock import Ui_CadInputDock


class LineEditFitler(QObject):
    """
    This class allows for internal shortcuts inside QLineEdit when they are being edited.
    """
    def __init__(self, cadInput):
        QObject.__init__(self)
        self.cadInput = cadInput

    def eventFilter(self, obj, event):
        if event.type() != QEvent.KeyPress:
            # execute the event
            return False
        obj.textEdited.emit(obj.text())
        self.cadInput.keyPressEvent(event)
        if event.isAccepted():
            # the event is intercepted, do not execute
            return True
        # nothing intercepted, execute the event (=> will write the text)
        return False


class CadInputWidget(QDockWidget, Ui_CadInputDock):
    """
    This is CadInput's main GUI widget. It displays the edit fields for entering numerical coordinates.
    """

    def __init__(self, iface):
        QDockWidget.__init__(self)
        self.setupUi(self)

        self.iface = iface

        # We want to get focus so KeyPressEvents can be processed (useful for internal shortcuts)
        self.setFocusPolicy(Qt.ClickFocus)

        # We connect the mapToolSet signal so we can enable/disable the widget
        self.iface.mapCanvas().mapToolSet.connect( self.maptoolChanged )

        # And we run it so it sets the right state upon loading
        self.maptoolChanged()

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

        #when parralel is selected, deselected perpendicular, and the otherway too
        self.widPar.toggled.connect(lambda state: disableIfEnabled(state,self.widPer))
        self.widPer.toggled.connect(lambda state: disableIfEnabled(state,self.widPar))

        self.widEnab.setDefaultAction(self.enableAction)

        self.linEditFilter = LineEditFitler(self)
        self.widA.installEventFilter(self.linEditFilter)
        self.widD.installEventFilter(self.linEditFilter)
        self.widX.installEventFilter(self.linEditFilter)
        self.widY.installEventFilter(self.linEditFilter)

        # not point at start, do not allow setting constraints
        self.enableConstraints(0)

        # And finally add to the MainWindow
        self.iface.mainWindow().addDockWidget(Qt.LeftDockWidgetArea, self)

    def closeEvent(self, event):
        self.widA.removeEventFilter(self.linEditFilter)
        self.widD.removeEventFilter(self.linEditFilter)
        self.widX.removeEventFilter(self.linEditFilter)
        self.widY.removeEventFilter(self.linEditFilter)
        event.accept()
    
    def keyPressEvent(self, event):
        """
        This implements the internal shortcuts when the focus is in the widget (e.g. on a QPushButton)
        """

        event.accept()
        if event.key() == Qt.Key_X:
            if event.modifiers() == Qt.AltModifier or event.modifiers() == Qt.ControlModifier:
                self.lockX.toggle()
            elif event.modifiers() == Qt.ShiftModifier:
                self.relX.toggle()
            else:
                self.widX.setFocus()
                self.widX.selectAll()
        elif event.key() == Qt.Key_Y:
            if event.modifiers() == Qt.AltModifier or event.modifiers() == Qt.ControlModifier:
                self.lockY.toggle()
            elif event.modifiers() == Qt.ShiftModifier:
                self.relY.toggle()
            else:
                self.widY.setFocus()
                self.widY.selectAll()
        elif event.key() == Qt.Key_A:
            if event.modifiers() == Qt.AltModifier or event.modifiers() == Qt.ControlModifier:
                self.lockA.toggle()
            elif event.modifiers() == Qt.ShiftModifier:
                self.relA.toggle()
            else:
                self.widA.setFocus()
                self.widA.selectAll()
        elif event.key() == Qt.Key_D:
            if event.modifiers() == Qt.AltModifier or event.modifiers() == Qt.ControlModifier:
                self.lockD.toggle()
            else:
                self.widD.setFocus()
                self.widD.selectAll()
        elif event.key() == Qt.Key_C:
            self.widC.toggle()
        elif event.key() == Qt.Key_P:
            if not self.par and not self.per:
                self.par = True
            elif self.par:
                self.per = True
            elif self.per:
                self.per = False
        elif event.key() == Qt.Key_Escape:
            self.unlockAll()
        else:
            event.ignore()


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

    def unlockAll(self):
        self.lx = False
        self.ly = False
        self.la = False
        self.ld = False

    def maptoolChanged(self):
        self.active = (self.iface.mapCanvas().mapTool() is not None and self.iface.mapCanvas().mapTool().isEditTool())


    def enableConstraints(self, nPoints):
        # absolute angle only possible with 1 previous point
        self.widA.setEnabled( nPoints>1 )
        self.lockA.setEnabled( nPoints>1 )
        # relative distance only available with 1 previous point
        self.widD.setEnabled( nPoints>1 )
        self.lockD.setEnabled( nPoints>1 )
        # relative coordinatesonly available with 1 previous point
        self.relX.setEnabled( nPoints>1 )
        self.relY.setEnabled( nPoints>1 )
        # relative angle only available with 2 previous point
        self.relA.setEnabled( nPoints>2 )


    """
    Those properties are just to lighten the code in CadEventFilter
    """

    # Basic properties
    @property
    def x(self): return floatOrZero(self.widX.text())
    @x.setter
    def x(self, value): self.widX.setText(str(value))

    @property
    def y(self): return floatOrZero(self.widY.text())
    @y.setter
    def y(self, value): self.widY.setText(str(value))

    @property
    def d(self): return floatOrZero(self.widD.text())
    @d.setter
    def d(self, value): self.widD.setText(str(value))

    @property
    def a(self): return floatOrZero(self.widA.text())
    @a.setter
    def a(self, value): self.widA.setText(str(value))

    #Lock properties
    @property
    def lx(self): return self.lockX.isEnabled() and self.lockX.isChecked()
    @lx.setter
    def lx(self, value): self.lockX.setChecked(value)

    @property
    def ly(self): return self.lockY.isEnabled() and self.lockY.isChecked()
    @ly.setter
    def ly(self, value): self.lockY.setChecked(value)

    @property
    def la(self): return self.lockA.isEnabled() and self.lockA.isChecked()
    @la.setter
    def la(self, value): self.lockA.setChecked(value)

    @property
    def ld(self): return self.lockD.isEnabled() and self.lockD.isChecked()
    @ld.setter
    def ld(self, value): self.lockD.setChecked(value)

    #Relative properties
    @property
    def rx(self): return self.relX.isEnabled() and self.relX.isChecked()
    @rx.setter
    def rx(self, value): self.relX.setChecked(value)

    @property
    def ry(self): return self.relY.isEnabled() and self.relY.isChecked()
    @ry.setter
    def ry(self, value): self.relY.setChecked(value)

    @property
    def ra(self): return self.relA.isEnabled() and  self.relA.isChecked()
    @ra.setter
    def ra(self, value): self.relA.setChecked(value)

    @property
    def rd(self): return True
    @rd.setter
    def rd(self, value): raise Exception


    #Misc properties
    @property
    def enabled(self): return self.enableAction.isChecked()
    @enabled.setter
    def enabled(self, value): self.enableAction.setChecked(value)

    @property
    def active(self): return self.isEnabled()
    @active.setter
    def active(self, value): self.setEnabled(value)

    @property
    def c(self): return self.widC.isChecked()
    @c.setter
    def c(self, value): self.widC.setChecked(value)

    @property
    def per(self): return self.widPer.isChecked()
    @per.setter
    def per(self, value): self.widPer.setChecked(value)

    @property
    def par(self): return self.widPar.isChecked()
    @par.setter
    def par(self, value): self.widPar.setChecked(value)

def floatOrZero(value):
    """
    Since float("") throws an error, we need to use this
    """
    try: return float(value)
    except: return 0.0



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

