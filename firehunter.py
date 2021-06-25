# -*- coding: utf-8 -*-

import re, processing, os.path, datetime
from qgis.PyQt.QtWidgets import QAction, QApplication
from qgis.PyQt.QtGui import QIcon
from qgis.core import Qgis, QgsApplication
from .resources import *
from .rectangleAreaTool import RectangleAreaTool
from .captureCoord import CaptureCoord
from .firehunter_processing_provider import firehunterProcessingProvider
from configparser import ConfigParser

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

        icon = QIcon(os.path.dirname(__file__) + '/twoday.png')
        self.twodayAction = QAction(icon, 'Make a Sentinel-2 2-day mosaic', self.iface.mainWindow())
        self.twodayAction.triggered.connect(self.runTwoDay)
        self.twodayAction.setEnabled(True)
        self.twodayAction.setCheckable(True)
        self.toolbar.addAction(self.twodayAction)
        self.iface.addPluginToRasterMenu(self.menu, self.twodayAction)

        icon = QIcon(os.path.dirname(__file__) + '/make-link.png')
        self.linkAction = QAction(icon, 'Make a Sentinel-hub link', self.iface.mainWindow())
        self.linkAction.triggered.connect(self.runMakeLink)
        self.linkAction.setEnabled(True)
        self.linkAction.setCheckable(True)
        self.toolbar.addAction(self.linkAction)
        self.iface.addPluginToRasterMenu(self.menu, self.linkAction)

        self.rectangleAreaTool = RectangleAreaTool(self.iface.mapCanvas(), self.rectangleAction)
        self.rectangleAreaTool.rectangleCreated.connect(self.run_r)
        self.twodayTool = RectangleAreaTool(self.iface.mapCanvas(), self.twodayAction)
        self.twodayTool.rectangleCreated.connect(self.run_t)
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
        self.iface.removePluginRasterMenu(self.menu, self.twodayAction)
        self.iface.removeToolBarIcon(self.twodayAction)
        QgsApplication.processingRegistry().removeProvider(self.firehunter_provider)
        del self.toolbar

    def run_r(self, startX, startY, endX, endY):
        if startX == endX and startY == endY:
            return
        extent = '%f,%f,%f,%f'%(startX, endX, startY, endY)
        today = datetime.date.today().strftime("%Y-%m-%d")
        [p_datefrompoint,p_interval_b,p_interval_a,p_singledate,p_composite,p_preyear,p_postyear,p_prefix,p_combi,p_band1,p_band2,p_band3,p_cloudfilter,p_cloud,p_vis_min,p_vis_max,p_visible] = self.get_config("set1")
        if p_datefrompoint:
            cur_Layer = self.iface.mapCanvas().currentLayer()
        else:
            cur_layer = ''
        self.iface.mapCanvas().setMapTool(self.prevMapTool)
        processing.execAlgorithmDialog('Fire hunter:Make a Sentinel-2 mosaic',
            {'EXTENT': extent, 
            'DATEFROMPOINT': p_datefrompoint,
            'INPUT': cur_Layer,
            'DATE': today,
            'INTERVAL_B': p_interval_b,
            'INTERVAL_A': p_interval_a,
            'SINGLEDATE': p_singledate,
            'COMPOSITE': p_composite,
            'PREYEAR': p_preyear,
            'POSTYEAR': p_postyear,
            'PREFIX': p_prefix,
            'COMBI': p_combi,
            'BAND1': p_band1,
            'BAND2': p_band2,
            'BAND3': p_band3,
            'CLOUDFILTER': p_cloudfilter,
            'CLOUD': p_cloud,
            'VIS_MIN': p_vis_min,
            'VIS_MAX': p_vis_max,
            'VISIBLE': p_visible
            })
        #self.iface.messageBar().pushMessage("", "Layer generation finished.", level=Qgis.Info, duration=4)

    def run_t(self, startX, startY, endX, endY):
        if startX == endX and startY == endY:
            return
        extent = '%f,%f,%f,%f'%(startX, endX, startY, endY)
        [p_datefrompoint,p_interval_b,p_interval_a,p_singledate,p_composite,p_preyear,p_postyear,p_prefix,p_combi,p_band1,p_band2,p_band3,p_cloudfilter,p_cloud,p_vis_min,p_vis_max,p_visible] = self.get_config("set2")
        if p_datefrompoint:
            cur_Layer = self.iface.mapCanvas().currentLayer()
            today = ''
        else:
            cur_layer = ''
            today = datetime.date.today().strftime("%Y-%m-%d")
        self.iface.mapCanvas().setMapTool(self.prevMapTool)
        processing.execAlgorithmDialog('Fire hunter:Make a Sentinel-2 mosaic',
            {'EXTENT': extent, 
            'DATEFROMPOINT': p_datefrompoint,
            'INPUT': cur_Layer,
            'DATE': today,
            'INTERVAL_B': p_interval_b,
            'INTERVAL_A': p_interval_a,
            'SINGLEDATE': p_singledate,
            'COMPOSITE': p_composite,
            'PREYEAR': p_preyear,
            'POSTYEAR': p_postyear,
            'PREFIX': p_prefix,
            'COMBI': p_combi,
            'BAND1': p_band1,
            'BAND2': p_band2,
            'BAND3': p_band3,
            'CLOUDFILTER': p_cloudfilter,
            'CLOUD': p_cloud,
            'VIS_MIN': p_vis_min,
            'VIS_MAX': p_vis_max,
            'VISIBLE': p_visible
            })
        #self.iface.messageBar().pushMessage("", "Layer generation finished.", level=Qgis.Info, duration=4)

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
                    self.iface.messageBar().pushMessage("", "Sentinel-Hub link copied to clipboard. {}".format(baselink), level=Qgis.Info, duration=4)
                else:
                    self.iface.messageBar().pushMessage("", "Unable to recognize date. Select a single-date layer.", level=Qgis.Warning, duration=4)
            else:
                self.iface.messageBar().pushMessage("", "Unable to recognize date. Select a single-date layer.", level=Qgis.Warning, duration=4)
        else:
            self.iface.messageBar().pushMessage("", "Unable to recognize date. Select a single-date layer.", level=Qgis.Warning, duration=4)
        #self.iface.mapCanvas().unsetMapTool(self.captureCoord)
        self.iface.mapCanvas().setMapTool(self.prevMapTool)
        self.linkAction.setChecked(False)

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

    def runTwoDay(self, b):
        if b:
            self.prevMapTool = self.iface.mapCanvas().mapTool()
            self.iface.mapCanvas().setMapTool(self.twodayTool)
        else:
            #self.iface.mapCanvas().unsetMapTool(self.captureCoord)
            self.iface.mapCanvas().setMapTool(self.prevMapTool)
            self.twodayAction.setChecked(False)

    def get_config(self, node):
        inifile = "firehunter.ini"
        param_names = ["datefrompoint", 
                        "interval_b",
                        "interval_a",
                        "singledate",
                        "composite",
                        "preyear",
                        "postyear",
                        "prefix",
                        "combi",
                        "band1",
                        "band2",
                        "band3",
                        "cloudfilter",
                        "cloud",
                        "vis_min",
                        "vis_max",
                        "visible"]
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, inifile)
        if os.path.exists(config_path):
            cfg = ConfigParser()
            cfg.read(config_path)
            param = [cfg.get(node, param_name) for param_name in param_names]
        else:
            param = [True, 7, 30, True, False, True, True, '', 4, 12, 7, 3, True, 1, 30, 7000, True]
        return param
