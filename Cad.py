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

import resources_rc

from CadInputWidget import CadInputWidget
from CadEventFilter import CadEventFilter
from CadPaintWidget import CadPaintWidget

from CadHelp import CadHelp


class Cad(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        self.iface = iface

    def initGui(self):
        #QgsMessageLog.logMessage("CadInput is being initialized","CadInput")
        
        # CadInputWidget : this widget displays the inputs allowing numerical entry
        self.inputwidget = CadInputWidget(self.iface)

        # CadEventFilter : this widget will filter the mouseEvents and constrain them if needed
        self.eventFilter = CadEventFilter(self.iface, self.inputwidget)

        # CadPaintWidget : this widget displays graphical informations in front of the mapCanvas
        self.paintwidget = CadPaintWidget(self.iface, self.inputwidget, self.eventFilter)



        #We need the canvas's viewport to track the mouse for mouseMoveEvents to happen
        self.iface.mapCanvas().viewport().setMouseTracking(True)

        #We install the eventFilter on the canvas's viewport to get the mouse events
        self.iface.mapCanvas().viewport().installEventFilter( self.eventFilter )

        #we install the eventFilter on the canvas itself to get the key events
        self.iface.mapCanvas().installEventFilter( self.eventFilter )

        #we add the paintwidget as a child of the mapCanvas (using a layout so it takes all available space)
        if self.iface.mapCanvas().layout() is None:
            layout = QHBoxLayout()
            layout.setContentsMargins( QMargins() )
            self.iface.mapCanvas().setLayout( layout )
        self.iface.mapCanvas().layout().addWidget( self.paintwidget )


        # Create help action 
        self.helpAction = QAction( QIcon(":/plugins/cadinput/resources/about.png"), u"Help", self.iface.mainWindow())
        self.helpAction.triggered.connect( self.doHelpAction )

        # Create enable action 
        self.enableAction = self.inputwidget.enableAction

        # Add menu and toolbars items
        self.iface.addPluginToMenu(u"&CadInput", self.helpAction)
        self.iface.addPluginToMenu(u"&CadInput", self.enableAction)
        self.iface.addToolBarIcon(self.enableAction)


    def unload(self):

        #we remove the eventFilters
        self.eventFilter.close()
        self.iface.mapCanvas().viewport().removeEventFilter( self.eventFilter )
        self.iface.mapCanvas().removeEventFilter( self.eventFilter )

        #and we remove the widgets also
        self.inputwidget.close()
        self.inputwidget.deleteLater()
        self.paintwidget.deleteLater()

        #and remove the item menu
        self.iface.removePluginMenu(u"&CadInput", self.helpAction)
        self.iface.removePluginMenu(u"&CadInput", self.enableAction)
        self.iface.removeToolBarIcon(self.enableAction)

    def doHelpAction(self):
        self.aboutWindow = CadHelp()
