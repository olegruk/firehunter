# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication
import processing, os.path
from .resources import *
from .rectangleAreaTool import RectangleAreaTool
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
        self.captureLatLonTool = CaptureLatLonTool(self.iface.mapCanvas(), self.linkAction)
        self.captureLatLonTool.latLonCaptured.connect(self.run_c)

        self.initProcessing()
        self.first_start = True

    def initProcessing(self):
        self.firehunter_provider = firehunterProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.firehunter_provider)
        self.makelink_provider = makeLinkProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.makelink_provider)

    def unload(self):
        self.iface.removePluginRasterMenu(self.menu, self.rectangleAction)
        self.iface.removeToolBarIcon(self.rectangleAction)
        self.iface.removePluginRasterMenu(self.menu, self.linkAction)
        self.iface.removeToolBarIcon(self.linkAction)
        QgsApplication.processingRegistry().removeProvider(self.firehunter_provider)
        QgsApplication.processingRegistry().removeProvider(self.makelink_provider)
        del self.toolbar

    def run_r(self, startX, startY, endX, endY):
        if startX == endX and startY == endY:
            return
        extent = '%f,%f,%f,%f'%(startX, endX, startY, endY)
        #self.iface.mapCanvas().unsetMapTool(self.rectangleAreaTool)
        self.iface.mapCanvas().setMapTool(self.prevMapTool)
        processing.execAlgorithmDialog('Fire hunter:Make a Sentinel-2 mosaic', {'EXTENT':extent})

    def run_c(self, lat, lon):
        baselink = 'https://apps.sentinel-hub.com/eo-browser/?zoom=14&lat=%f&lng=%f&themeId=DEFAULT-THEME'%(lat, lon)
        #self.iface.mapCanvas().unsetMapTool(self.captureLatLonTool)
        self.iface.mapCanvas().setMapTool(self.prevMapTool)
        processing.execAlgorithmDialog('Fire hunter:Make a Sentinel-hub link', {'BASE_LINK':baselink})

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
            self.iface.mapCanvas().setMapTool(self.captureLatLonTool)
        else:
            #self.iface.mapCanvas().unsetMapTool(self.captureLatLonTool)
            self.iface.mapCanvas().setMapTool(self.prevMapTool)

