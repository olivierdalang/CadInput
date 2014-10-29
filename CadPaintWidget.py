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

class CadPaintWidget(QgsMapCanvasItem):

    def __init__(self, mapCanvas, inputWidget, cadPointList):
        QgsMapCanvasItem.__init__(self, mapCanvas)
        self.inputWidget = inputWidget
        self.cadPointList = cadPointList
        self.mapCanvas = mapCanvas

        self.pLocked = QPen(QColor(100,100,255, 255), 2, Qt.DashLine)
        self.pConstruction1 = QPen(QColor(100,255,100, 150), 2, Qt.DashLine)
        self.pConstruction2 = QPen(QColor(100,255,100, 255), 2, Qt.DashLine)
        self.pSnap = QPen(QColor(255,175,100,150), 10)
        self.pSnapLine = QPen(QColor(200,100,50,150), 1, Qt.DashLine)
        self.pCursor = QPen(QColor(100,255,100, 255), 2)

        self.mapCanvas.extentsChanged.connect(self.updateRect)

    def close(self):
        self.mapCanvas.extentsChanged.disconnect(self.updateRect)

    def updateRect(self):
        self.setRect( self.mapCanvas.extent() )
        self.setVisible( self.inputWidget.active )

    def paint(self, painter, option, widget):
        """
        Paints the visual feedback (painting is done in screen coordinates).
        """

        pointListLength = len(self.cadPointList)
        curPoint = self.cadPointList.currentPoint()
        prevPoint = self.cadPointList.previousPoint()
        penulPoint = self.cadPointList.penultimatePoint()
        snapPoint = self.cadPointList.snapPoint
        snapSegment = self.cadPointList.snapSegment
        
        mupp = self.mapCanvas.getCoordinateTransform().mapUnitsPerPixel()
            
        if math.isnan( mupp ) or not self.inputWidget.active or not self.inputWidget.enabled:
            #on loading QGIS, it seems QgsMapToPixel is not ready and return NaNs...
            return

        curPointPix, prevPointPix, penulPointPix, snapSegmentPix1, snapSegmentPix2 = None, None, None, None, None

        if curPoint is not None:
            curPointPix = self.toCanvasCoordinates(curPoint)
        if prevPoint is not None:
            prevPointPix = self.toCanvasCoordinates(prevPoint)
        if penulPoint is not None:
            penulPointPix = self.toCanvasCoordinates(penulPoint)
        if snapSegment is not None:
            snapSegmentPix1 = self.toCanvasCoordinates(snapSegment[1])
            snapSegmentPix2 = self.toCanvasCoordinates(snapSegment[2])

        #This is used so the whole widget updates rather than just the painEvent region (probably under-optimal since painEvent is probably called twice)
        # self.update()

        painter.setRenderHints(QPainter.Antialiasing)

        #Draw point snap
        if snapPoint is not None:

            snapPointPix = self.toCanvasCoordinates(snapPoint)
            painter.setPen( self.pSnap )
            painter.drawEllipse( snapPointPix, 10, 10 )

            if curPoint is not None:
                painter.setPen( self.pSnapLine )
                painter.drawLine(   snapPointPix.x(),
                                    snapPointPix.y(),
                                    curPointPix.x(),
                                    curPointPix.y() )

        #Draw segment snap
        if snapSegment is not None:
            painter.setPen( self.pSnap )
            painter.drawLine(   snapSegmentPix1.x(),
                                snapSegmentPix1.y(),
                                snapSegmentPix2.x(),
                                snapSegmentPix2.y() )

            if curPoint is not None:
                painter.setPen( self.pSnapLine )
                painter.drawLine(   snapSegmentPix1.x(),
                                    snapSegmentPix1.y(),
                                    curPointPix.x(),
                                    curPointPix.y() )


        #Draw segment par/per input
        if (self.inputWidget.per or self.inputWidget.par) and self.cadPointList.snapSegment is not None:
            painter.setPen( self.pConstruction2 )
            painter.drawLine(   snapSegmentPix1.x(),
                                snapSegmentPix1.y(),
                                snapSegmentPix2.x(),
                                snapSegmentPix2.y() )


        #Draw angle
        if pointListLength>1:
            if self.inputWidget.ra and pointListLength>2:
                a0 = math.atan2( -(prevPoint.y()-penulPoint.y()), prevPoint.x()-penulPoint.x() )
                a = a0-math.radians(self.inputWidget.a)
            else:
                a0 = 0
                a = -math.radians(self.inputWidget.a)

            painter.setPen( self.pConstruction2 )
            painter.drawArc(    prevPointPix.x()-20,
                                prevPointPix.y()-20,
                                40, 40,
                                16*math.degrees(-a0),
                                16*self.inputWidget.a  )
            painter.drawLine(   prevPointPix.x(),
                                prevPointPix.y(),
                                prevPointPix.x()+60*math.cos(a0),
                                prevPointPix.y()+60*math.sin(a0)  )

            if self.inputWidget.la:
                painter.setPen( self.pLocked )
                d = max(self.boundingRect().width(),self.boundingRect().height())
                painter.drawLine(   prevPointPix.x() - d*math.cos(a),
                                    prevPointPix.y() - d*math.sin(a),
                                    prevPointPix.x() + d*math.cos(a),
                                    prevPointPix.y() + d*math.sin(a) )

        #Draw distance
        if pointListLength>1 and self.inputWidget.ld:
            painter.setPen( self.pLocked )
            r = self.inputWidget.d / mupp
            painter.drawEllipse( prevPointPix, r, r )

        #Draw x
        if self.inputWidget.lx:
            painter.setPen( self.pLocked )
            if self.inputWidget.rx:
                if pointListLength>1:
                    x = self.inputWidget.x / mupp + prevPointPix.x()
                else:
                    x = None
            else:
                x = self.toCanvasCoordinates( QgsPoint( self.inputWidget.x, 0) ).x()
            if x is not None:
                painter.drawLine(   x,
                                    0,
                                    x,
                                    self.boundingRect().height() )

        #Draw y
        if self.inputWidget.ly:
            painter.setPen( self.pLocked )
            if self.inputWidget.ry:
                if pointListLength>1:
                    # y is reversed!
                    y = -self.inputWidget.y / mupp + prevPointPix.y()
                else:
                    y = None
            else:
                y = self.toCanvasCoordinates( QgsPoint( 0, self.inputWidget.y) ).y()
            if y is not None:
                painter.drawLine(   0,
                                    y,
                                    self.boundingRect().width(),
                                    y )

        #Draw constr
        if not self.inputWidget.par and not self.inputWidget.per:
            if prevPoint is not None:
                painter.setPen( self.pConstruction2 )
                painter.drawLine(   prevPointPix.x(),
                                    prevPointPix.y(),
                                    curPointPix.x(),
                                    curPointPix.y()  )

            if penulPoint is not None:
                painter.setPen( self.pConstruction1 )
                painter.drawLine(   penulPointPix.x(),
                                    penulPointPix.y(),
                                    prevPointPix.x(),
                                    prevPointPix.y()  )

        if curPoint is not None:
            painter.setPen( self.pCursor )
            painter.drawLine(   curPointPix.x()-5,
                                curPointPix.y()-5,
                                curPointPix.x()+5,
                                curPointPix.y()+5  )
            painter.drawLine(   curPointPix.x()-5,
                                curPointPix.y()+5,
                                curPointPix.x()+5,
                                curPointPix.y()-5  )





