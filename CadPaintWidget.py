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
import random

class CadPaintWidget(QWidget):

    def __init__(self, iface, inputwidget, eventfilter):
        QObject.__init__(self,inputwidget)
        self.iface = iface
        self.inputwidget = inputwidget
        self.eventfilter = eventfilter

        #We don't want this widget to deal with mouseEvents
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        #Nor with key events
        self.setFocusPolicy(Qt.NoFocus)


    def _t(self, qgspoint):
        return self.iface.mapCanvas().getCoordinateTransform().transform(qgspoint)
    def _tX(self, x):
        r = self._t(QgsPoint(x,0)).x()
        return r
    def _tY(self, y):
        r = self._t(QgsPoint(0,y)).y()
        return r
    def _f(self, v):
        r = v/self.iface.mapCanvas().getCoordinateTransform().mapUnitsPerPixel()
        return r

    def paintEvent(self, paintEvent):
        """
        Paints the visual feedback (painting is done in screen coordinates).
        """

        if math.isnan( self._tX(0) ) or not self.inputwidget.active or not self.inputwidget.enabled:
            #on loading QGIS, it seems QgsMapToPixel is not ready and return NaNs...
            return

        #This is used so the whole widget updates rather than just the painEvent region (probably under-optimal since painEvent is probably called twice)
        self.update()

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
 
        pLocked = QPen(QColor(100,100,255, 255), 2, Qt.DashLine) 
        pConstruction1 = QPen(QColor(100,255,100, 150), 2, Qt.DashLine)
        pConstruction2 = QPen(QColor(100,255,100, 255), 2, Qt.DashLine)
        pSnap = QPen(QColor(255,175,100,150), 10)
        pSnapLine = QPen(QColor(200,100,50,150), 1, Qt.DashLine)
        pCursor = QPen(QColor(100,255,100, 255), 2)

        #Draw snap
        if self.eventfilter.snapPoint is not None:

            x = self._tX( self.eventfilter.snapPoint.x())
            y = self._tY( self.eventfilter.snapPoint.y())

            painter.setPen( pSnap )
            painter.drawEllipse(    x-10,
                                    y-10,
                                    20,
                                    20  )

            painter.setPen( pSnapLine )
            painter.drawLine(   x,
                                y,
                                self._tX( self.eventfilter.p3.x()),
                                self._tY( self.eventfilter.p3.y())  )


        if self.eventfilter.snapSegment is not None:
            painter.setPen( pSnap )

            painter.drawLine(   self._tX( self.eventfilter.snapSegment[1].x()),
                                self._tY( self.eventfilter.snapSegment[1].y()),
                                self._tX( self.eventfilter.snapSegment[2].x()),
                                self._tY( self.eventfilter.snapSegment[2].y())  )


            painter.setPen( pSnapLine )
            painter.drawLine(   self._tX( self.eventfilter.snapSegment[1].x()),
                                self._tY( self.eventfilter.snapSegment[1].y()),
                                self._tX( self.eventfilter.p3.x()),
                                self._tY( self.eventfilter.p3.y())  )


        #Draw segment
        if (self.inputwidget.per or self.inputwidget.par) and self.eventfilter.snapSegment is not None:
            painter.setPen( pLocked )

            painter.drawLine(   self._tX( self.eventfilter.snapSegment[1].x()),
                                self._tY( self.eventfilter.snapSegment[1].y()),
                                self._tX( self.eventfilter.snapSegment[2].x()),
                                self._tY( self.eventfilter.snapSegment[2].y())  )


        #Draw angle
        if self.inputwidget.ra:                
            a0 = math.atan2( -(self.eventfilter.p2.y()-self.eventfilter.p1.y()), self.eventfilter.p2.x()-self.eventfilter.p1.x() )
            a = a0-math.radians(self.inputwidget.a)
        else:
            a0 = 0
            a = -math.radians(self.inputwidget.a)

        painter.setPen( pConstruction2 )
        painter.drawArc(    self._tX( self.eventfilter.p2.x())-20,
                            self._tY( self.eventfilter.p2.y())-20,
                            40, 40,
                            16*math.degrees(-a0),
                            16*self.inputwidget.a  )
        painter.drawLine(   self._tX( self.eventfilter.p2.x()),
                            self._tY( self.eventfilter.p2.y()),
                            self._tX( self.eventfilter.p2.x())+60*math.cos(a0),
                            self._tY( self.eventfilter.p2.y())+60*math.sin(a0)  )

        if self.inputwidget.la:
            painter.setPen( pLocked )
            painter.drawLine(   self._tX( self.eventfilter.p2.x())-self.width()*math.cos(a),
                                self._tY( self.eventfilter.p2.y())-self.width()*math.sin(a),
                                self._tX( self.eventfilter.p2.x())+self.width()*math.cos(a),
                                self._tY( self.eventfilter.p2.y())+self.width()*math.sin(a)  )



        #Draw distance
        if self.inputwidget.ld:
            painter.setPen( pLocked )
            painter.drawEllipse(    self._tX( self.eventfilter.p2.x() - self.inputwidget.d ),
                                    self._tY( self.eventfilter.p2.y() + self.inputwidget.d ),
                                    self._f( 2.0*self.inputwidget.d ),
                                    self._f( 2.0*self.inputwidget.d )  )


        #Draw x
        if self.inputwidget.lx:
            painter.setPen( pLocked )
            if self.inputwidget.rx:
                x = self._tX( self.eventfilter.p2.x()+self.inputwidget.x )
            else:   
                x = self._tX( self.inputwidget.x )
            painter.drawLine(   x,
                                0,
                                x,
                                self.height() )

        #Draw y
        if self.inputwidget.ly:
            painter.setPen( pLocked )
            if self.inputwidget.ry:
                y = self._tY( self.eventfilter.p2.y()+self.inputwidget.y )
            else:   
                y = self._tY( self.inputwidget.y )
            painter.drawLine(   0,
                                y,
                                self.width(),
                                y )

        #Draw constr
        if not self.inputwidget.par and not self.inputwidget.per:
            painter.setPen( pConstruction2 )
            painter.drawLine(   self._tX( self.eventfilter.p2.x()),
                                self._tY( self.eventfilter.p2.y()),
                                self._tX( self.eventfilter.p3.x()),
                                self._tY( self.eventfilter.p3.y())  )

            painter.setPen( pConstruction1 )
            painter.drawLine(   self._tX( self.eventfilter.p1.x()),
                                self._tY( self.eventfilter.p1.y()),
                                self._tX( self.eventfilter.p2.x()),
                                self._tY( self.eventfilter.p2.y())  )

        painter.setPen( pCursor )
        painter.drawLine(   self._tX( self.eventfilter.p3.x())-5,
                            self._tY( self.eventfilter.p3.y())-5,
                            self._tX( self.eventfilter.p3.x())+5,
                            self._tY( self.eventfilter.p3.y())+5  )
        painter.drawLine(   self._tX( self.eventfilter.p3.x())-5,
                            self._tY( self.eventfilter.p3.y())+5,
                            self._tX( self.eventfilter.p3.x())+5,
                            self._tY( self.eventfilter.p3.y())-5  )









