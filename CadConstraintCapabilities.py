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


class CadConstraintCapabilities():
    def __init__(self):
        self.absoluteAngle = False
        self.distance = False
        self.relativePos = False
        self.relativeAngle = False

    def setAbsoluteAngle(self, value):
        hasChanged = self.absoluteAngle != value
        self.absoluteAngle = value
        return hasChanged

    def setDistance(self, value):
        hasChanged = self.distance != value
        self.distance = value
        return hasChanged

    def setRelativePos(self, value):
        hasChanged = self.relativePos != value
        self.relativePos = value
        return hasChanged

    def setRelativeAngle(self, value):
        hasChanged = self.relativeAngle != value
        self.relativeAngle = value
        return hasChanged

    def update(self, nPoints):
        hasChanged = False
        if nPoints>1:
            hasChanged |= self.setAbsoluteAngle(True)
            hasChanged |= self.setDistance(True)
            hasChanged |= self.setRelativePos(True)
        else:
            hasChanged |= self.setAbsoluteAngle(False)
            hasChanged |= self.setDistance(False)
            hasChanged |= self.setRelativePos(False)
        if nPoints>2:
            hasChanged |= self.setRelativeAngle(True)
        else:
            hasChanged |= self.setRelativeAngle(False)
        return hasChanged
