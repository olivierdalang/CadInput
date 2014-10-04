# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CadInput
                                 A QGIS plugin
 Provides CAD-like input globally : digitize features with precise numerical input for the angle, the distance, and easily make widCuctions lines
                              -------------------
        begin                : 2014-02-05
        copyright            : (C) 2014 by Olivier Dalang
        email                :  olivier.dalang@gmail.com
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
from math import sqrt


class CadIntersection():

    @staticmethod
    def LineIntersectionAtX(linePoint1, linePoint2, x):
        x1 = linePoint1.x()
        y1 = linePoint1.y()
        x2 = linePoint2.x()
        y2 = linePoint2.y()
        dx = x2 - x1
        dy = y2 - y1
        if dx==0:
            y = y1
        else:
            y = y1+(dy * (x-x1) ) / dx
        return y


    @staticmethod
    def LineIntersectionAtY(linePoint1, linePoint2, y):
        x1 = linePoint1.x()
        y1 = linePoint1.y()
        x2 = linePoint2.x()
        y2 = linePoint2.y()
        dx = x2 - x1
        dy = y2 - y1
        if dy==0:
            x = x1
        else:
            x = x1+(dx * (y-y1) ) / dy
        return x


    @staticmethod
    def CircleLineIntersection(linePoint1, linePoint2, circleCenter, r):
        # formula taken from http://mathworld.wolfram.com/Circle-LineIntersection.html

        x1 = linePoint1.x()-circleCenter.x()
        y1 = linePoint1.y()-circleCenter.y()
        x2 = linePoint2.x()-circleCenter.x()
        y2 = linePoint2.y()-circleCenter.y()

        dx = x2-x1
        dy = y2-y1
        dr = sqrt(dx**2+dy**2)
        d = x1*y2-x2*y1

        def sgn(x): return -1 if x<0 else 1

        DISC = r**2 * dr**2 - d**2

        if DISC<=0:
            #no intersection or tangeant
            return None, None

        else:
            #first possible point
            ax = circleCenter.x() + (d*dy+sgn(dy)*dx*sqrt(r**2*dr**2-d**2))/(dr**2)
            ay = circleCenter.y() + (-d*dx+abs(dy)*sqrt(r**2*dr**2-d**2))/(dr**2)

            #second possible point
            bx = circleCenter.x() + (d*dy-sgn(dy)*dx*sqrt(r**2*dr**2-d**2))/(dr**2)
            by = circleCenter.y() + (-d*dx-abs(dy)*sqrt(r**2*dr**2-d**2))/(dr**2)

            return QgsPoint(ax,ay), QgsPoint(bx,by)
