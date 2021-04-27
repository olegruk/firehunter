# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QAction, QApplication
from qgis.PyQt.QtGui import QIcon
from qgis.core import Qgis, QgsApplication
import re, processing, os.path
from .resources import *
from .rectangleAreaTool import RectangleAreaTool
from .captureCoord import CaptureCoord
from .firehunter_processing_provider import firehunterProcessingProvider

class FireHunter:

    def __init__(self, iface):
        self.iface = iface
        self.menu = '&Fire Hunter'
        self.provider = None
        self.first_start = None
        self.toolbar = self.iface.addToolBar('Fire Hunter')
        self.toolbar.setObjectName('FireHunter')

    def initGui(self):
        icon = QIcon(os.path.dirname(__file__) + '/firehunter.png')
        self.rectangleAction = QAction(icon, 'Make a Sentinel-2 mosaic', self.iface.mainWindow())
        self.rectangleAction.triggered.connect(self.runRectangle)
        self.rectangleAction.setEnabled(True)
        self.rectangleAction.setCheckable(True)
        self.toolbar.addAction(self.rectangleAction)
        self.iface.addPluginToRasterMenu(self.menu, self.rectangleAction)

        icon = QIcon(os.path.dirname(__file__) + '/make-link.png')
        self.linkAction = QAction(icon, 'Make a Sentinel-hub link', self.iface.mainWindow())
        self.linkAction.triggered.connect(self.runMakeLink)
        self.linkAction.setEnabled(True)
        self.linkAction.setCheckable(True)
        self.toolbar.addAction(self.linkAction)
        self.iface.addPluginToRasterMenu(self.menu, self.linkAction)

        self.rectangleAreaTool = RectangleAreaTool(self.iface.mapCanvas(), self.rectangleAction)
        self.rectangleAreaTool.rectangleCreated.connect(self.run_r)
        self.captureCoord = CaptureCoord(self.iface)
        self.captureCoord.captureStopped.connect(self.run_c)

        self.initProcessing()
        self.first_start = True

    def initProcessing(self):
        self.firehunter_provider = firehunterProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.firehunter_provider)
        #self.makelink_provider = makeLinkProcessingProvider()
        #QgsApplication.processingRegistry().addProvider(self.makelink_provider)

    def unload(self):
        self.iface.removePluginRasterMenu(self.menu, self.rectangleAction)
        self.iface.removeToolBarIcon(self.rectangleAction)
        self.iface.removePluginRasterMenu(self.menu, self.linkAction)
        self.iface.removeToolBarIcon(self.linkAction)
        QgsApplication.processingRegistry().removeProvider(self.firehunter_provider)
        #QgsApplication.processingRegistry().removeProvider(self.makelink_provider)
        del self.toolbar

    def run_r(self, startX, startY, endX, endY):
        if startX == endX and startY == endY:
            return
        extent = '%f,%f,%f,%f'%(startX, endX, startY, endY)
        #self.iface.mapCanvas().unsetMapTool(self.rectangleAreaTool)
        self.iface.mapCanvas().setMapTool(self.prevMapTool)
        processing.execAlgorithmDialog('Fire hunter:Make a Sentinel-2 mosaic', {'EXTENT':extent})

    def run_c(self, lat, lon):
        sel_lay = self.iface.layerTreeView().selectedLayers()
        if sel_lay:
            sel_lay = sel_lay[0].name()
            date_start = re.search(r'S2SRC_\d\d\d\d-\d\d-\d\d', sel_lay)
        if date_start:
            date_start = date_start[0]
            if len(date_start) == 16:
                date_start = date_start[6:]
                baselink = 'https://apps.sentinel-hub.com/eo-browser/?zoom=13&lat=%f&lng=%f&themeId=DEFAULT-THEME&datasetId=S2L1C&fromTime=%sT00%%3A00%%3A00.000Z&toTime=%sT23%%3A59%%3A59.999Z&layerId=6-SWIR'%(lat, lon, date_start, date_start)
                clipboard = QApplication.clipboard()
                clipboard.setText(baselink)
                self.iface.messageBar().pushMessage("", "Coordinate captured. {}".format(baselink), level=Qgis.Info, duration=4)
            else:
                self.iface.messageBar().pushMessage("", "Unable to recognize date. Select a single-date layer.", level=Qgis.Warning, duration=4)
        else:
            self.iface.messageBar().pushMessage("", "Unable to recognize date. Select a single-date layer.", level=Qgis.Warning, duration=4)
        #self.iface.mapCanvas().unsetMapTool(self.captureCoord)
        self.iface.mapCanvas().setMapTool(self.prevMapTool)
        self.linkAction.setChecked(False)
        #processing.execAlgorithmDialog('Fire hunter:Make a Sentinel-hub link', {'BASE_LINK':baselink})

    def runRectangle(self, b):
        if b:
            self.prevMapTool = self.iface.mapCanvas().mapTool()
            self.iface.mapCanvas().setMapTool(self.rectangleAreaTool)
        else:
            #self.iface.mapCanvas().unsetMapTool(self.rectangleAreaTool)
            self.iface.mapCanvas().setMapTool(self.prevMapTool)

    def runMakeLink(self, b):
        if b:
            self.prevMapTool = self.iface.mapCanvas().mapTool()
            self.iface.mapCanvas().setMapTool(self.captureCoord)
        else:
            #self.iface.mapCanvas().unsetMapTool(self.captureCoord)
            self.iface.mapCanvas().setMapTool(self.prevMapTool)
            self.linkAction.setChecked(False)
