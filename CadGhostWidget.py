# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CadInput
                                 A QGIS plugin
 Provides CAD-like input globally : digitize features with precise numerical input for the angle, the distance, and easily make constructions lines
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
import math
import ast
import operator as op

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *


class GhostWidget(QWidget):
    """
    This class is a transparent Widget in from of the QMapCanvas.
    It captures all mouse input, displays the cad-like input drawing aid and sends translated mouse events to QMapCanvas
    """

    def __init__(self, iface, cadwidget):
        QWidget.__init__(self)
        self.iface = iface
        self.cadwidget = cadwidget

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.ClickFocus)

        self.suspendForPan = False


        self.p1 = QgsPoint() # previous click
        self.p2 = QgsPoint() # last click
        self.p3 = QgsPoint() # current position

        self.x = 0
        self.y = 0
        self.d = 0
        self.a = 0

    def _active(self):
        if self.iface.mapCanvas().mapTool() is not None:
            return self.iface.mapCanvas().mapTool().isEditTool()
        return None

    ###########################
    ##### INPUT EVENTS ########
    ###########################

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.suspendForPan and self._active():

            self.p3 = self.manageP3(self.toMap( event.pos() ) )

            event = QMouseEvent( event.type(), self.toPixels(self.p2), event.button(), event.buttons(), event.modifiers() )

            if not self.cadwidget.c:
                self.iface.mapCanvas().mousePressEvent(event)

            self.p1 = self.p2
            self.p2 = self.p3
        else:
            if event.button() == Qt.MidButton:
                self.suspendForPan = True
            self.iface.mapCanvas().mousePressEvent(event)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and not self.suspendForPan and self._active():

            event = QMouseEvent( event.type(), self.toPixels(self.p2), event.button(), event.buttons(), event.modifiers() )

            if not self.cadwidget.c:
                self.iface.mapCanvas().mouseReleaseEvent(event)
        else:
            if event.button() == Qt.RightButton:
                self.cadwidget.lx = False
                self.cadwidget.ly = False
                self.cadwidget.la = False
                self.cadwidget.ld = False
            if event.button() == Qt.MidButton:
                self.suspendForPan = False
            self.iface.mapCanvas().mouseReleaseEvent(event)
    def mouseMoveEvent(self, event):
        if not self.suspendForPan and self._active():

            self.p3 = self.manageP3(self.toMap( event.pos() ))
            self.update() #runs paintEvent

            event = QMouseEvent( event.type(), self.toPixels(self.p3), event.button(), event.buttons(), event.modifiers() )

            if not self.cadwidget.c:
                self.iface.mapCanvas().mouseMoveEvent(event)
        else:
            self.iface.mapCanvas().mouseMoveEvent(event)
    def wheelEvent(self, event):
        self.iface.mapCanvas().wheelEvent(event)
    def keyPressEvent(self, event):
        """
        Shortcuts to the cadwidget
        """

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
            self.cadwidget.constr.toggle()
        else:
            self.iface.mapCanvas().keyPressEvent(event)


    ###############################
    ##### COORDINATE TOOLS ########
    ###############################

    def manageP3(self, p3):
        """
        This method returns a point constrained by the w's settings and, by the way, updates the w's displayed values.
        """


        #X
        if self.cadwidget.lx:
            if self.cadwidget.rx:
                p3.setX( self.p2.x() + self.cadwidget.x )
            else:
                p3.setX( self.cadwidget.x )
        else:
            if self.cadwidget.rx:
                self.cadwidget.x = p3.x()-self.p2.x()
            else:
                self.cadwidget.x = p3.x()

        #Y
        if self.cadwidget.ly:
            if self.cadwidget.ry:
                p3.setY( self.p2.y() + self.cadwidget.y )
            else:
                p3.setY( self.cadwidget.y )
        else:
            if self.cadwidget.ry:
                self.cadwidget.y = p3.y()-self.p2.y()
            else:
                self.cadwidget.y = p3.y()


        #A
        dx =  p3.x()-self.p2.x()
        dy =  p3.y()-self.p2.y()

        if self.cadwidget.la:
            a = self.cadwidget.a/180.0*math.pi
            if self.cadwidget.ra:
                # We compute the angle relative to the last segment (0° is aligned with last segment)
                lastA = math.atan2(self.p2.y() - self.p1.y(), self.p2.x() - self.p1.x())
                a = lastA+a
                cosA = math.cos( a )
                sinA = math.sin( a )
                v1 = [ cosA, sinA ]
                v2 = [ dx, dy ]
                vP = v1[0]*v2[0]+v1[1]*v2[1]
                p3.set( self.p2.x()+cosA*vP, self.p2.y()+sinA*vP)
            else:
                # We compute the absolute angle (0° is horizontal to the right)
                cosA = math.cos( a )
                sinA = math.sin( a )
                v1 = [ cosA, sinA ]
                v2 = [ dx, dy ]
                vP = v1[0]*v2[0]+v1[1]*v2[1]
                p3.set( self.p2.x()+cosA*vP, self.p2.y()+sinA*vP)
        else:
            if self.cadwidget.ra:
                lastA = math.atan2(self.p2.y() - self.p1.y(), self.p2.x() - self.p1.x())
                self.cadwidget.a = (math.atan2( dy, dx )-lastA)/math.pi*180
            else:
                self.cadwidget.a = math.atan2( dy, dx )/math.pi*180


        #D
        dx =  p3.x()-self.p2.x()
        dy =  p3.y()-self.p2.y()

        if self.cadwidget.ld:
            vP = self.cadwidget.d / math.sqrt( dx*dx + dy*dy )
            p3.set( self.p2.x()+dx*vP,  self.p2.y()+dy*vP )
        else:
            self.cadwidget.d = math.sqrt( dx*dx + dy*dy )

        return p3
    def toMap(self, qpoint):
        snapper = QgsMapCanvasSnapper(self.iface.mapCanvas())
        snapped = snapper.snapToBackgroundLayers(qpoint)
        if len(snapped[1]) > 0:
            # It seems to be necessary to create a new QgsPoint from the snapping result
            return QgsPoint(snapped[1][0].snappedVertex.x(), snapped[1][0].snappedVertex.y())

        return self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates( qpoint )
    def toPixels(self, qgspoint):
        try:
            p = self.iface.mapCanvas().getCoordinateTransform().transform( qgspoint )
            return QPoint( int(p.x()), int(p.y()) )
        except ValueError:
            #this happens sometimes at loading, it seems the mapCanvas is not ready and returns a point at NaN;NaN
            return QPoint()


    #######################
    ##### PAINTING ########
    #######################

    def _t(self, qgspoint):
        return self.iface.mapCanvas().getCoordinateTransform().transform(qgspoint)
    def _tX(self, x):
        return self._t(QgsPoint(x,0)).x()
    def _tY(self, y):
        return self._t(QgsPoint(0,y)).y()
    def _f(self, v):
        return v/self.iface.mapCanvas().getCoordinateTransform().mapUnitsPerPixel()

    def paintEvent(self, paintEvent):

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        pNeutral = QPen(QColor(0,0,100,100), 1)  
        pLocked = QPen(QColor(100,100,255, 150), 2, Qt.DashLine) 
        pConstruction = QPen(QColor(100,255,100, 150), 2, Qt.DashLine) 

        #Draw angle
        if self.cadwidget.la:

            if self.cadwidget.ra:                
                a0 = math.atan2( -(self.p2.y()-self.p1.y()), self.p2.x()-self.p1.x() )
                a = a0-math.radians(self.cadwidget.a)
            else:
                a0 = 0
                a = -math.radians(self.cadwidget.a)


            painter.setPen( pNeutral )
            painter.drawArc(    self._tX( self.p2.x())-20,
                                self._tY( self.p2.y())-20,
                                40, 40,
                                16*math.degrees(-a0),
                                16*self.cadwidget.a  )
            painter.drawLine(   self._tX( self.p2.x()),
                                self._tY( self.p2.y()),
                                self._tX( self.p2.x())+60*math.cos(a0),
                                self._tY( self.p2.y())+60*math.sin(a0)  )
            painter.setPen( pLocked )
            painter.drawLine(   self._tX( self.p2.x())-self.width()*math.cos(a),
                                self._tY( self.p2.y())-self.width()*math.sin(a),
                                self._tX( self.p2.x())+self.width()*math.cos(a),
                                self._tY( self.p2.y())+self.width()*math.sin(a)  )



        #Draw distance
        if self.cadwidget.ld:
            painter.setPen( pLocked )
            painter.drawEllipse(    self._tX( self.p2.x() - self.cadwidget.d ),
                                    self._tY( self.p2.y() + self.cadwidget.d ),
                                    self._f( 2.0*self.cadwidget.d ),
                                    self._f( 2.0*self.cadwidget.d )  )


        #Draw x
        if self.cadwidget.lx:
            painter.setPen( pLocked )
            if self.cadwidget.rx:
                x = self._tX( self.p2.x()+self.cadwidget.x )
            else:   
                x = self._tX( self.cadwidget.x )
            painter.drawLine(   x,
                                0,
                                x,
                                self.height() )

        #Draw y
        if self.cadwidget.ly:
            painter.setPen( pLocked )
            if self.cadwidget.ry:
                y = self._tY( self.p2.y()+self.cadwidget.y )
            else:   
                y = self._tY( self.cadwidget.y )
            painter.drawLine(   0,
                                y,
                                self.width(),
                                y )

        #Draw constr
        if self.cadwidget.c:

            painter.setPen( pConstruction )
            painter.drawLine(   self._tX( self.p1.x()),
                                self._tY( self.p1.y()),
                                self._tX( self.p2.x()),
                                self._tY( self.p2.y())  )
            painter.drawLine(   self._tX( self.p2.x()),
                                self._tY( self.p2.y()),
                                self._tX( self.p3.x()),
                                self._tY( self.p3.y())  )

            painter.drawLine(   self._tX( self.p3.x())-5,
                                self._tY( self.p3.y())-5,
                                self._tX( self.p3.x())+5,
                                self._tY( self.p3.y())+5  )
            painter.drawLine(   self._tX( self.p3.x())-5,
                                self._tY( self.p3.y())+5,
                                self._tX( self.p3.x())+5,
                                self._tY( self.p3.y())-5  )




