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

from CadWidget import CadWidget
from CadGhostWidget import GhostWidget

class CadInput(QObject):
    """
    This class loads the UI and instantiate all other classes.
    """

    updateUi = pyqtSignal(float, float, float)

    def __init__(self, iface):
        QObject.__init__(self)
        self.iface = iface

    def initGui(self):

        QgsMessageLog.logMessage("init","CadInput")

        # CadWidget : this widget displays the inputs allowing numerical entry
        self.cadwidget = CadWidget(self.iface)
        self.dockwidget = QDockWidget("CadInput")
        self.dockwidget.setWidget(self.cadwidget)
        self.iface.mainWindow().addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)

        # GhostWidget : this widget is placed as child of the QgsCanvas and is used to intercept all mouseEvents as well as to display graphical feedback
        self.ghostwidget = GhostWidget(self.iface, self.cadwidget)

        # we use a layout so the ghostwidget spans to the whole qcanvas space
        layout = QHBoxLayout()
        layout.setContentsMargins( QMargins() )
        layout.addWidget( self.ghostwidget )
        self.iface.mapCanvas().setLayout( layout )

        # We want the ghostwidget to redraw when the values of the cadwidget are edited
        self.cadwidget.valueEdited.connect(self.ghostwidget.repaint)


    def unload(self):
        #UNLOAD seems no to work
        self.ghostwidget.setParent(None)
        self.cadwidget.setParent(None)
        self.dockwidget.setParent(None)






