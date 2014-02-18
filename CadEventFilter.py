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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from CadIntersection import *

import math


class CadEventFilter(QObject):
    """
    This class manages the events for the MapCanvas.

    It is responsible of constraining events according to the 
    inputWidget's values and to update the inputWidget's values 
    according to the constrained mouse position.
    """


    def __init__(self, iface, cadPointList, inputWidget, paintWidget):
        QObject.__init__(self)
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        self.inputWidget = inputWidget
        self.paintWidget = paintWidget
        self.cadPointList = cadPointList

        #snapping hack
        self.storeOtherSnapping = None #holds the layer's snapping options when snapping is suspended or None if snappig is not suspended
        self.otherSnappingStored = False

        # snap layers list
        self.snapper = None # the snapper used to get snapped points from the map canvas. We can't use 
        self.updateSnapper()
        self.mapCanvas.layersChanged.connect(self.updateSnapper)
        self.mapCanvas.scaleChanged.connect(self.updateSnapper)
        QgsProject.instance().readProject.connect(self.updateSnapper)
        QgsProject.instance().snapSettingsChanged.connect(self.updateSnapper) # TODO : does not work ! see http://hub.qgis.org/issues/9465

    def close(self):
        self.mapCanvas.layersChanged.disconnect(self.updateSnapper)
        self.mapCanvas.scaleChanged.disconnect(self.updateSnapper)
        QgsProject.instance().readProject.disconnect(self.updateSnapper)
        QgsProject.instance().snapSettingsChanged.disconnect(self.updateSnapper)

    def updateSnapper(self):
        """
            Updates self.snapper to take into consideration layers changes, layers not displayed because of the scale *TODO* and the user's input */TODO*
            @note : it's a shame we can't get QgsMapCanvasSnapper().mSnapper which would replace all code below (I guess)
        """
        snapperList = []
        scale = self.iface.mapCanvas().mapRenderer().scale()
        curLayer = self.iface.legendInterface().currentLayer()
        layers = self.iface.mapCanvas().layers()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer.hasGeometryType():
                if not layer.hasScaleBasedVisibility() or layer.minimumScale() < scale <= layer.maximumScale():
                    (layerid, enabled, snapType, tolUnits, tol, avoidInt) = QgsProject.instance().snapSettingsForLayer(layer.id())                    
                    if not enabled:
                        continue
                    snapLayer = QgsSnapper.SnapLayer()
                    snapLayer.mLayer = layer
                    snapLayer.mSnapTo = snapType
                    snapLayer.mTolerance = tol
                    snapLayer.mUnitType = tolUnits
                    # put current layer on top
                    if layer is curLayer:
                        snapperList.insert(0, snapLayer)
                    else:
                        snapperList.append(snapLayer)

        self.snapper = QgsSnapper(self.mapCanvas.mapRenderer())
        self.snapper.setSnapLayers(snapperList)
        self.snapper.setSnapMode(QgsSnapper.SnapWithResultsWithinTolerances)


    ############################
    ##### EVENT MANAGEMENT #####
    ############################

    def eventFilter(self, obj, event):
        # We only run this if the event is spontaneous,
        # which means that it was generated by the OS.
        # This way, the event we create below won't be processed (which would be an inifinite loop)
        if not event.spontaneous():
            return QObject.eventFilter(self, obj, event)

        # MOUSE MOVE OR LEFT CLICK
        if ( self.inputWidget.active and self.inputWidget.enabled and
                    (  (event.type() == QEvent.MouseMove and event.button() != Qt.MidButton) or
                       (event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton) or
                       (event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton) ) ):
            
            # Get the snaps
            (self.cadPointList.snapPoint, self.cadPointList.snapSegment) = self._toMapSnap( event.pos() )

            # Set the current mouse position (either from snapPoint, from snapSegment, or regular coordinate transform)
            if self.cadPointList.snapPoint is not None:
                curPoint = QgsPoint(self.cadPointList.snapPoint)
            elif self.cadPointList.snapSegment is not None:
                curPoint = self.cadPointList.snapSegment[0]
            else:
                curPoint = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates( event.pos() )

            curPoint = self._constrain(curPoint)
            self.cadPointList.updateCurrentPoint(curPoint)


            # A perpendicular or parallel mode
            if self.inputWidget.par or self.inputWidget.per:
                #A. Set segment mode (we set the angle)
                if event.type() == QEvent.MouseButtonPress:
                    self._alignToSegment()
                elif event.type() == QEvent.MouseButtonRelease and self.cadPointList.snapSegment:
                    self.inputWidget.par = False
                    self.inputWidget.per = False

            # B standard input mode
            else:

                # B1. Construction mode
                if self.inputWidget.c:
                    pass

                # B2. Normal input mode
                else:
                    if event.type() == QEvent.MouseButtonPress or event.type() == QEvent.MouseButtonRelease:
                        #B2a. Mouse press input mode
                        self.createSnappingPoint()
                        modifiedEvent = QMouseEvent( event.type(), self._toPixels(curPoint), event.button(), event.buttons(), event.modifiers() )
                        QCoreApplication.sendEvent(obj,modifiedEvent)
                        self.removeSnappingPoint()

                    else:
                        #B2B. Mouse move input mode
                        modifiedEvent = QMouseEvent( event.type(), self._toPixels(curPoint), event.button(), event.buttons(), event.modifiers() )
                        QCoreApplication.sendEvent(obj,modifiedEvent)

                # We unlock all the inputs, since we don't want locking to stay for the next point (actually, sometimes we do, this could be an option)
                if event.type() == QEvent.MouseButtonRelease:
                    self.inputWidget.unlockAll()

                # In input mode (B), we register the last points for following relative calculation in case of mousePress
                if event.type() == QEvent.MouseButtonRelease:
                    self.cadPointList.newPoint()

            # update the map canvas item
            self.paintWidget.updateRect()

            # By returning True, we inform the eventSystem that the event must not be sent further (since a new event has been sent through QCoreApplication)
            return True

        # KEYPRESS
        elif self.inputWidget.active and event.type() == QEvent.KeyPress:
            # remove last point
            if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
                self.cadPointList.removeLastPoint()
                # update the map canvas item
                self.paintWidget.updateRect()
                return False
            # otherwise redirect all key inputs to the inputWidget
            self.inputWidget.keyPressEvent(event)
            # if inputWidget intercepted the event, this will True (event not propagated further)
            return event.isAccepted()

        # RIGHT CLICK
        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.RightButton:
            # cancel digitization on right click
            self.cadPointList.empty()
            self.cadPointList.snapSegment = None # segment snapped at current position (if any)
            self.cadPointList.snapPoint = None # point snapped at current position (if any)
            QCoreApplication.sendEvent(obj,event)
            return True

        # OTHERWISE
        else:
            #In case we don't manage this type of event, we return the normal implementation
            return QObject.eventFilter(self, obj, event)


    ########################
    ##### CONSTRAINING #####
    ########################

    def _constrain(self, point):
        """
        This method returns a point constrained by the w's settings and, by the way, updates the w's displayed values.
        """
        previousPoint = self.cadPointList.previousPoint()
        penulPoint = self.cadPointList.penultimatePoint()
        dx, dy, ddx, ddy, dist = None, None, None, None, None


        #################
        # X constrain
        if self.inputWidget.lx:
            if self.inputWidget.rx:
                point.setX( previousPoint.x() + self.inputWidget.x )
            else:
                point.setX( self.inputWidget.x )

            if self.cadPointList.snapSegment is not None and not self.inputWidget.ly:
                # we will magnietize to the intersection of that segment and the lockedX !
                y = CadIntersection.LineIntersectionAtX( self.cadPointList.snapSegment[1], self.cadPointList.snapSegment[2], point.x() )
                point.setY( y )
        else:
            if self.inputWidget.rx:
                self.inputWidget.x = point.x() - previousPoint.x()
            else:
                self.inputWidget.x = point.x()

        #################
        # Y constrain
        if self.inputWidget.ly:
            if self.inputWidget.ry:
                point.setY( previousPoint.y() + self.inputWidget.y )
            else:
                point.setY( self.inputWidget.y )

            if self.cadPointList.snapSegment is not None and not self.inputWidget.lx:
                # we will magnietize to the intersection of that segment and the lockedY !
                x = CadIntersection.LineIntersectionAtY( self.cadPointList.snapSegment[1], self.cadPointList.snapSegment[2], point.y() )
                point.setX( x )
        else:
            if self.inputWidget.ry:
                self.inputWidget.y = point.y() - previousPoint.y()

            else:
                self.inputWidget.y = point.y()

        #################
        # Angle constrain
        if len(self.cadPointList)>1:
            dx = point.x() - previousPoint.x()
            dy = point.y() - previousPoint.y()
        if self.inputWidget.ra and len(self.cadPointList)>2:
            ddx = previousPoint.x() - penulPoint.x()
            ddy = previousPoint.y() - penulPoint.y()

        if len(self.cadPointList)>1 and self.inputWidget.la:
            a = self.inputWidget.a/180.0*math.pi
            if self.inputWidget.ra and len(self.cadPointList)>2:
                # We compute the angle relative to the last segment (0° is aligned with last segment)
                a += math.atan2(ddy, ddx)
            else:
                # if relative mode and not enough points: do absolute angle
                pass

            cosA = math.cos( a )
            sinA = math.sin( a )
            v1 = [ cosA, sinA ]
            v2 = [ dx, dy ]
            vP = v1[0]*v2[0]+v1[1]*v2[1]
            point.set( previousPoint.x()+cosA*vP, previousPoint.y()+sinA*vP)

            if self.cadPointList.snapSegment is not None and not self.inputWidget.ld:
                # we will magnietize to the intersection of that segment and the lockedAngle !

                l1 = QLineF(previousPoint.x(), previousPoint.y(), previousPoint.x()+math.cos(a), previousPoint.y()+math.sin(a))
                l2 = QLineF(self.cadPointList.snapSegment[1].x(), self.cadPointList.snapSegment[1].y(), self.cadPointList.snapSegment[2].x() ,self.cadPointList.snapSegment[2].y())

                intP = QPointF()
                ang = l1.angleTo(l2)
                t = 0.0001
                # TODO : this may cause some accuracy problem ?
                if l1.intersect(l2, intP) == QLineF.UnboundedIntersection and not (ang < t or ang > 360-t or (ang > 180-t and ang < 180+t) ):
                    point.set( intP.x(), intP.y() )
        else:
            if len(self.cadPointList)>1:
                if self.inputWidget.ra and len(self.cadPointList)>2:
                    lastA = math.atan2(ddy, ddx)
                else:
                    lastA = 0
                self.inputWidget.a = (math.atan2( dy, dx )-lastA)/math.pi*180
            else:
                self.inputWidget.a = None

        #################
        # Distance constrain
        if len(self.cadPointList)>1:
            dx = point.x() - previousPoint.x()
            dy = point.y() - previousPoint.y()
            dist = math.sqrt(point.sqrDist(previousPoint))

        if len(self.cadPointList)>1 and self.inputWidget.ld:
            if dist == 0:
                # handle case where mouse is over origin and distance constraint is enabled
                # take arbitrary horizontal line
                point.set( previousPoint.x()+self.inputWidget.d, previousPoint.y() )
            else:
                vP = self.inputWidget.d / dist
                point.set( previousPoint.x()+dx*vP,  previousPoint.y()+dy*vP )

            if self.cadPointList.snapSegment is not None and not self.inputWidget.la:
                # we will magnietize to the intersection of that segment and the lockedDistance !
                p1, p2 = CadIntersection.CircleLineIntersection(self.cadPointList.snapSegment[1], self.cadPointList.snapSegment[2],
                                                                previousPoint, self.inputWidget.d)
                #we snap to the nearest intersection
                if p1 is not None:
                    if point.sqrDist(p1) < point.sqrDist(p2):
                        point.set( p1.x(), p1.y() )
                    else:
                        point.set( p2.x(), p2.y() )
        else:
            self.inputWidget.d = dist

        #Update the widget's x&y values (for display only)
        if self.inputWidget.rx:
            if len(self.cadPointList)>1:
                self.inputWidget.x = point.x() - previousPoint.x()
            else:
                self.inputWidget.rx = False
        if not self.inputWidget.rx:
            self.inputWidget.x = point.x()

        if self.inputWidget.ry:
            if len(self.cadPointList)>1:
                self.inputWidget.y = point.y() - previousPoint.y()
            else:
                self.inputWidget.ry = False
        if not self.inputWidget.ry:
            self.inputWidget.y = point.y()

        return point


    def _alignToSegment(self):
        """
        Set's the CadWidget's angle value to be parrelel to self.cadPointList.snapSegment's angle
        """
        
        previousPoint = self.cadPointList.previousPoint()
        penulPoint = self.cadPointList.penultimatePoint()

        # do not authorize per or par if there is no previous point
        if previousPoint is None or self.cadPointList.snapSegment is None:
            return

        angle = math.atan2( self.cadPointList.snapSegment[1].y()-self.cadPointList.snapSegment[2].y(), self.cadPointList.snapSegment[1].x()-self.cadPointList.snapSegment[2].x() )
        if self.inputWidget.ra:
            lastangle = math.atan2(previousPoint.y()-penulPoint.y(),previousPoint.x()-penulPoint.x())
            angle -= lastangle

        if self.inputWidget.par:
            pass
        elif self.inputWidget.per:
            angle += math.pi / 2.0

        self.inputWidget.la = True
        self.inputWidget.a = math.degrees(angle)
    

    #####################################
    ##### COORDINATE TRANSFORMATIONS ####
    #####################################

    def _toMapSnap(self, qpoint):
        """
        returns the current snapped point (if any) and the current snapped segment (if any) in map coordinates
        The current snapped segment is returned as (snapped point on segment, startPoint, endPoint)
        """
        ok, snappingResults = self.snapper.snapPoint(qpoint, [])
        for result in snappingResults:
            if result.snappedVertexNr != -1:
                return QgsPoint(result.snappedVertex), None
        if len(snappingResults):
            output = (QgsPoint(snappingResults[0].snappedVertex), QgsPoint(snappingResults[0].beforeVertex), QgsPoint(snappingResults[0].afterVertex))
            return None, output
        else:
            return None, None

    def _toPixels(self, qgspoint):
        """
        Given a point in project's coordinates, returns a point in screen (pixel) coordinates
        """
        try:
            p = self.iface.mapCanvas().getCoordinateTransform().transform( qgspoint )
            return QPoint( int(p.x()), int(p.y()) )
        except ValueError:
            #this happens sometimes at loading, it seems the mapCanvas is not ready and returns a point at NaN;NaN
            return QPoint()




    #########################
    ##### SNAPPING HACK #####
    #########################
    
    def createSnappingPoint(self):
        """
        This method creates a point that will be snapped by the next click so that the point will be at model precision and not at screen precision.
        It also disables all the other layer's snapping so they won't interfere. Those are reset in rmeoveSnapping point.
        """
        activeLayer = self.iface.activeLayer()

        #store and remove all the snapping options
        self.disableBackgroundSnapping()

        try:
            provider = self.memoryLayer.dataProvider()
        except (RuntimeError, AttributeError):
            #RuntimeError : if the user removed the layer, the underlying c++ object will be deleted
            #AttributeError : if self.memory is None
            self.cleanLayers("(cadinput_techical_snap_layer)")
            self.memoryLayer = QgsVectorLayer("point", "(cadinput_techical_snap_layer)", "memory")
            QgsMapLayerRegistry.instance().addMapLayer(self.memoryLayer, False)
            provider = self.memoryLayer.dataProvider()

        QgsProject.instance().blockSignals(True) #we don't want to refresh the snapping UI
        QgsProject.instance().setSnapSettingsForLayer(self.memoryLayer.id(),  True, QgsSnapper.SnapToVertex , QgsTolerance.Pixels, 20.0, False )
        QgsProject.instance().blockSignals(False) #we don't want to refresh the snapping UI

        feature = QgsFeature()
        feature.setGeometry( QgsGeometry.fromPoint( self.cadPointList.currentPoint() ) )
        provider.addFeatures([feature])

        self.memoryLayer.updateExtents()

        self.iface.setActiveLayer(activeLayer)

    def removeSnappingPoint(self):
        """
        This methods empties the snapping layer.
        It must be called after createSnappingPoint (once the snapping has been done), since it also reenables the other layer's snapping
        """

        #empty the layer
        provider = self.memoryLayer.dataProvider()
        features = provider.getFeatures( QgsFeatureRequest() )

        for feature in features:
            provider.deleteFeatures([feature.id()])

        #In 2.2, this will be  (untested):
        #provider = self.memoryLayer.dataProvider()
        #provider.deleteFeatures( self.memoryLayer.allFeatureIds() )


        #restore the snapping options
        self.restoreBackgroundSnapping()

    def disableBackgroundSnapping(self):
        """
        Stores (for latter restoring) and then remove all the snapping options.
        """


        if self.otherSnappingStored:
            QgsMessageLog.logMessage("WARNING : restoreBackgroundSnapping was not called before disableBackgroundSnapping ! We don't store it again...")
        else:
            self.otherSnappingStored = True
            QgsProject.instance().blockSignals(True) #we don't want to refresh the snapping UI
            self.storeOtherSnapping = dict()
            layers = self.iface.mapCanvas().layers()
            for layer in layers:
                if layer.type() == QgsMapLayer.VectorLayer and layer.hasGeometryType():
                    self.storeOtherSnapping[layer.id()] = QgsProject.instance().snapSettingsForLayer(layer.id())
                    QgsProject.instance().setSnapSettingsForLayer(layer.id(),False,0,0,0,False)

            QgsProject.instance().blockSignals(False) #we don't want to refresh the snapping UI

    def restoreBackgroundSnapping(self):
        """
        Restores previously stored snapping options
        """

        self.otherSnappingStored = False

        QgsProject.instance().blockSignals(True) #we don't want to refresh the snapping UI

        for layerId in self.storeOtherSnapping:
            options = self.storeOtherSnapping[layerId]
            QgsProject.instance().setSnapSettingsForLayer(layerId,options[1],options[2],options[3],options[4],options[5])

        QgsProject.instance().blockSignals(False) #we don't want to refresh the snapping UI

    def cleanLayers(self, layernameToClean):
        """
        Cleans the old memory layers (all layer having layernameToClean for name) to avoid proliferation of unused memory layers.
        """

        # Clean the old memory layers
        for name in QgsMapLayerRegistry.instance().mapLayers():
            layer = QgsMapLayerRegistry.instance().mapLayers()[name]
            if layer.name() == layernameToClean:
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())



