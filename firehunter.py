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
        self.rectangleAction = QAction(icon, 'Make a Sentinel-2 mosaic around firepoint by rectangle selection', self.iface.mainWindow())
        self.rectangleAction.triggered.connect(self.runRectangle)
        self.rectangleAction.setEnabled(True)
        self.rectangleAction.setCheckable(True)
        self.toolbar.addAction(self.rectangleAction)
        self.iface.addPluginToRasterMenu(self.menu, self.rectangleAction)

        self.rectangleAreaTool = RectangleAreaTool(self.iface.mapCanvas(), self.rectangleAction)
        self.rectangleAreaTool.rectangleCreated.connect(self.run)

        self.initProcessing()
        self.first_start = True

    def initProcessing(self):
        self.provider = firehunterProcessingProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        self.iface.removePluginRasterMenu(self.menu, self.rectangleAction)
        self.iface.removeToolBarIcon(self.rectangleAction)
        QgsApplication.processingRegistry().removeProvider(self.provider)
        del self.toolbar

    def run(self, startX, startY, endX, endY):
        if startX == endX and startY == endY:
            return
        extent = '%f,%f,%f,%f'%(startX, endX, startY, endY)
        #self.iface.mapCanvas().unsetMapTool(self.rectangleAreaTool)
        self.iface.mapCanvas().setMapTool(self.prevMapTool)
        processing.execAlgorithmDialog('firehunter:S2_image', {'EXTENT':extent})

    def runRectangle(self, b):
        if b:
            self.prevMapTool = self.iface.mapCanvas().mapTool()
            self.iface.mapCanvas().setMapTool(self.rectangleAreaTool)
        else:
            #self.iface.mapCanvas().unsetMapTool(self.rectangleAreaTool)
            self.iface.mapCanvas().setMapTool(self.prevMapTool)

