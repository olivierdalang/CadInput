# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CadInput
                                 A QGIS plugin
 Provides CAD-like input globally : digitize features with precise numerical input for the angle, the distance, and easily make widCuctions lines
                              -------------------
        begin                : 2014-02-04
        copyright            : (C) 2014 by Denis Rouzaud
        email                : denis.rouzaud@gmail.com
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

from qgis.core import QgsPoint

class CadPointList(list):
    """
    Sub-class of list to save list of QgsPoint
    """
    def __init__(self, inputWidget):
        list.__init__(self)
        self.inputWidget = inputWidget
        self.snapPoint = None
        self.snapSegment = None

    def empty(self):
        self[:] = []
        self.inputWidget.enableConstraints(len(self))
        self.inputWidget.unlockAll()

    def updateCurrentPoint(self, point):
        if len(self)>0:
            self[0] = point
        else:
            self.insert(0, point)
            self.inputWidget.enableConstraints(len(self))

    def newPoint(self):
        self.insert(0, self[0])
        self.inputWidget.enableConstraints(len(self))

    def removeLastPoint(self):
        print len(self)
        if len(self)>1:
            del self[1]
            self.inputWidget.enableConstraints(len(self))

    def currentPoint(self):
        if len(self):
            return self[0]
        else:
            return None

    def previousPoint(self):
        if len(self) > 1:
            return self[1]
        else:
            return None

    def penultimatePoint(self):
        if len(self) > 2:
            return self[2]
        else:
            return None


