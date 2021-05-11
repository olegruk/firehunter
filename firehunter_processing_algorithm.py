# -*- coding: utf-8 -*-

"""
/***************************************************************************
 *   FirehunterProcessingAlgorithm                                         *
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *   It based on Google Earth Engine plugin by Gennadii Donchyts.          *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProject,
                       QgsRasterLayer,
                       QgsLayerTreeLayer,
                       QgsFeature,
                       QgsVectorLayer,
                       QgsProcessing,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterDateTime,
                       QgsProcessingAlgorithm,
                       QgsCoordinateReferenceSystem,
                       QgsMapLayerType)
from processing.core.Processing import Processing
import os.path, json,pyproj

class firehunterProcessingAlgorithm(QgsProcessingAlgorithm):

    EXTENT = 'EXTENT'
    DATEFROMPOINT = 'DATEFROMPOINT'
    INPUT = 'INPUT'
    DATE1 = 'DATE1'
    INTERVAL = 'INTERVAL'
    SINGLEDATE = 'SINGLEDATE'
    COMPOSITE = 'COMPOSITE'
    PREFIX = 'PREFIX'
    COMBI = 'COMBI'
    BAND1 = 'BAND1'
    BAND2 = 'BAND2'
    BAND3 = 'BAND3'
    CLOUDFILTER = 'CLOUDFILTER'
    CLOUD = 'CLOUD'
    VIS_MIN = 'VIS_MIN'
    VIS_MAX = 'VIS_MAX'
    VISIBLE = 'VISIBLE'
    OUTPUT = 'OUTPUT'
#    VIS_GAMMA = 'VIS_GAMMA'

    combinations = {}

    def initAlgorithm(self, config=None):

        self.bandlist = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B10', 'B11', 'B12']
        self.combinations = ['True color', 'False color', 'False color (urban)', 'SWIR', 'Custom']
        self.combi_dict = {'True color':['B4','B3','B2'], 'False color':['B8','B4','B3'], 'False color (urban)':['B12','B11','B4'], 'SWIR':['B12','B8A','B4'], 'Custom':['B12','B8','B4']}
        self.addParameter(QgsProcessingParameterExtent(self.EXTENT, 'Mosaic extent:'))
        self.addParameter(QgsProcessingParameterBoolean(self.DATEFROMPOINT, 'Get dates interval from points layer.', defaultValue=False, optional=False))
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, 'Points layer:', types=[QgsProcessing.TypeVectorPoint], optional=True))
        self.addParameter(QgsProcessingParameterDateTime(self.DATE1, 'Date (last date for mosaic):', type=1))
        self.addParameter(QgsProcessingParameterNumber(self.INTERVAL, 'Interval (days before "Date"):', defaultValue=7, optional=False, minValue=1, maxValue=31))
        self.addParameter(QgsProcessingParameterBoolean(self.SINGLEDATE, 'Generate single-date layers.', defaultValue=True, optional=False))
        self.addParameter(QgsProcessingParameterBoolean(self.COMPOSITE, 'Generate composite layer.', defaultValue=False, optional=False))
        self.addParameter(QgsProcessingParameterString(self.PREFIX, 'Layer prefix:', defaultValue='', optional=True))
        self.addParameter(QgsProcessingParameterEnum(self.COMBI, 'Channels combination:', self.combinations, defaultValue=len(self.combinations)-1))
        self.addParameter(QgsProcessingParameterEnum(self.BAND1, 'Band1 (red):', self.bandlist, defaultValue=12))
        self.addParameter(QgsProcessingParameterEnum(self.BAND2, 'Band2 (green):', self.bandlist, defaultValue=7))
        self.addParameter(QgsProcessingParameterEnum(self.BAND3, 'Band3 (blue):', self.bandlist, defaultValue=3))
        self.addParameter(QgsProcessingParameterBoolean(self.CLOUDFILTER, 'Apply cloud filter.', defaultValue=True, optional=False))
        self.addParameter(QgsProcessingParameterNumber(self.CLOUD, 'Cloudness:', defaultValue=50, optional=False, minValue=0, maxValue=100))
        self.addParameter(QgsProcessingParameterNumber(self.VIS_MIN, 'Vis_min:', defaultValue=30, optional=False, minValue=0, maxValue=10000))
        self.addParameter(QgsProcessingParameterNumber(self.VIS_MAX, 'Vis_max:', defaultValue=7000, optional=False, minValue=0, maxValue=10000))
        self.addParameter(QgsProcessingParameterBoolean(self.VISIBLE, 'Make result layer visible.', defaultValue=True, optional=False))
#        self.addParameter(QgsProcessingParameterNumber(self.VIS_GAMMA, 'Vis_gamma:', defaultValue=1.7, optional=False, minValue=0, maxValue=10))
       
    def processAlgorithm(self, parameters, context, feedback):
        Processing.initialize()
        import ee
        ee.Initialize()

        crs = context.project().crs()
        final_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        bbox = self.parameterAsExtent(parameters, self.EXTENT, context, crs)
        bbox_prj = self.bbox_for_ee_collection(bbox, crs, final_crs)
        aoi=ee.FeatureCollection(ee.Geometry.Polygon(bbox_prj))

        interval = self.parameterAsInt(parameters, self.INTERVAL, context)
        get_date_from_point = self.parameterAsBoolean(parameters, self.DATEFROMPOINT, context)
        date1 = self.parameterAsDateTime(parameters, self.DATE1, context)
        if get_date_from_point:
            point_layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
            bbox_geom = self.parameterAsExtentGeometry(parameters, self.EXTENT, context, crs)
            if type(point_layer) != QgsVectorLayer:
                in_layer = self.parameterAsSource(parameters, self.INPUT, context)
                point_layer = self.copy_features(in_layer, final_crs, feedback)
            date1, date2 = self.date_from_point(point_layer, bbox_geom, date1, crs, feedback)
           
        #Параметры визуализации
        cloudiness = self.parameterAsInt(parameters, self.CLOUD, context)
        combi = self.parameterAsEnum(parameters, self.COMBI, context)
        if combi == len(self.combinations)-1:
            r_band = self.bandlist[self.parameterAsEnum(parameters, self.BAND1, context)]
            g_band = self.bandlist[self.parameterAsEnum(parameters, self.BAND2, context)]
            b_band = self.bandlist[self.parameterAsEnum(parameters, self.BAND3, context)]
        else:
            r_band = self.combi_dict[self.combinations[combi]][0]
            g_band = self.combi_dict[self.combinations[combi]][1]
            b_band = self.combi_dict[self.combinations[combi]][2]
        bands = [r_band,g_band,b_band]
        vis_min = self.parameterAsInt(parameters, self.VIS_MIN, context)
        vis_max = self.parameterAsInt(parameters, self.VIS_MAX, context)
        #vis_gamma = self.parameterAsDouble(parameters, self.VIS_GAMMA, context)
        vis_gamma = 1.7
        visParams = {'bands': bands,'min': vis_min,'max': vis_max,'gamma': vis_gamma}
        is_visible = self.parameterAsBoolean(parameters, self.VISIBLE, context)

        generate_composite = self.parameterAsBoolean(parameters, self.COMPOSITE, context)
        if generate_composite:
            date_end = date1.toString("yyyy-MM-dd")
            date_start = date1.addDays(-interval).toString("yyyy-MM-dd")
            #Выбираем коллекцию снимков  и фильтруем по общей облачности
            cloud_filter = self.parameterAsBoolean(parameters, self.CLOUDFILTER, context)
            if cloud_filter:
                collection = ee.ImageCollection('COPERNICUS/S2').filterMetadata('CLOUDY_PIXEL_PERCENTAGE','not_greater_than', cloudiness).filterBounds(aoi).map(self.filterCloudSentinel2)
            else:
                collection = ee.ImageCollection('COPERNICUS/S2').filterBounds(aoi)
            #Определяем размер коллекции
            col_size1 = collection.size().getInfo()
            #Создадим медианный композит и обрежем по аои
            dated_col = collection.filterDate(date_start,date_end)
            col_size2 = dated_col.size().getInfo()
            if col_size2 > 0:
                im1 = dated_col.median().clipToCollection(aoi)
                prefix = self.parameterAsString(parameters, self.PREFIX, context)
                layer_name_1 = 'S2SRC_%s_%s'%(date_start,date_end)
                if prefix:
                    layer_name_1 = prefix + '-' +layer_name_1
                #добавим на карту
                self.addLayer(date_start,im1,visParams,layer_name_1,is_visible)

        generate_singledate = self.parameterAsBoolean(parameters, self.SINGLEDATE, context)
        if generate_singledate:
            for i in range(interval+1):
                date_start = date1.addDays(-i).toString("yyyy-MM-dd")
                date_end = date1.addDays(-i+1).toString("yyyy-MM-dd")
                collection = ee.ImageCollection('COPERNICUS/S2').filterBounds(aoi)
                dated_col = collection.filterDate(date_start,date_end)
                #im = collection.filterDate(date_start).mean()#median().clipToCollection(aoi)
                col_size = dated_col.size().getInfo()
                if col_size > 0:
                    im = dated_col.median().clipToCollection(aoi)
                    prefix = self.parameterAsString(parameters, self.PREFIX, context)
                    layer_name = 'S2SRC_%s'%date_start
                    if prefix:
                        layer_name = prefix + '-' +layer_name
                    self.addLayer(date_start,im,visParams,layer_name,is_visible)

#        #Парметры каналы, исходное изображение, АОИ, шкала (чем больше тем быстрее),перцентили)
#        layer_name_2 = 'Sent-2-%s-%s-stretch'%(date_start,date_end)
#        s2str=self.stretcher(bands,im1.updateMask(im1.gt(0)),aoi,1500,3,97)
#        #извлекаем rgb и определяем его как image
#        im2 = ee.Image(s2str.get('imRGB')).clipToCollection(aoi)
#        #добавим на карту
#        self.addLayer(im2,{},layer_name_2,is_visible)

        return {self.OUTPUT: bands}

    def copy_features(self, in_layer, crs, feedback):
        uri_str = "Point?crs=" + crs.authid() + "&field=date_time:datetime"
        out_layer = QgsVectorLayer(uri_str, "out_layer", "memory")
        feat = QgsFeature()
        for f in in_layer.getFeatures():
            feat.setGeometry(f.geometry())
            feat.setAttributes([f.attribute('date_time')])
            out_layer.dataProvider().addFeature(feat)
        feedback.pushConsoleInfo('Selected points: %s'%str(out_layer.featureCount()))
        return out_layer

    def date_from_point(self, point_layer, bbox_geom, date, crs, feedback):
        import processing
        uri_str = "Polygon?crs=" + crs.authid() + "&field=name:string(5)"
        tmp_layer = QgsVectorLayer(uri_str, "tmp_layer", "memory")
        tmp_provider = tmp_layer.dataProvider()
        feat = QgsFeature()
        feat.setGeometry(bbox_geom)
        feat.setAttributes(['temp'])
        tmp_provider.addFeatures([feat])

        result = processing.run('qgis:intersection', {'INPUT': point_layer, 'OVERLAY': tmp_layer, 'INPUT_FIELDS': ['acq_date', 'date_time'], 'OUTPUT': 'memory:'})
        features = result['OUTPUT'].getFeatures()
        f_count = result['OUTPUT'].featureCount()
        feedback.pushConsoleInfo('Points in intersection for detecting date: %s'%str(f_count))
        date_list = []
        total = 100.0 / f_count if f_count else 0
        for current, f in enumerate(features):
            if feedback.isCanceled():
                break
            #date_list.append(f.attribute('acq_date'))
            date_list.append(f.attribute('date_time'))
            feedback.setProgress(int(current * total))
        if date_list:
            max_date = max(date_list)
            min_date = min(date_list)
        else:
            max_date = date
            min_date = date

        return max_date, min_date

    def bbox_for_ee_collection(self, bbox, in_crs, out_crs):
        proj_in = pyproj.Proj(init=in_crs.authid())
        proj_out = pyproj.Proj(init=out_crs.authid())
        xmin, ymin = pyproj.transform(proj_in, proj_out, bbox.xMinimum(), bbox.yMinimum())
        xmax, ymax = pyproj.transform(proj_in, proj_out, bbox.xMaximum(), bbox.yMaximum())
        bbox_reproj = [[[xmin, ymax],
                        [xmin, ymin],
                        [xmax, ymin],
                        [xmax, ymax]]]

        return bbox_reproj

    def stretcher(self, bands, im, AOI, scale, range1, range2):
        import ee
        stats = im.select(bands).clipToCollection(AOI).reduceRegion(
        reducer=ee.Reducer.percentile([range1, range2]), 
        geometry=AOI,
        scale=scale,
        maxPixels= 1e15)
        imRGB = im.select(bands).visualize(
        min=ee.List([stats.get(bands[0]+'_p'+str(range1)), stats.get(bands[1]+'_p'+str(range1)), stats.get(bands[2]+'_p'+str(range1))]), 
        max=ee.List([stats.get(bands[0]+'_p'+str(range2)), stats.get(bands[1]+'_p'+str(range2)), stats.get(bands[2]+'_p'+str(range2))]), 
        )
        return im.set('imRGB', imRGB)#Добавляем rgb к исходным каналам в виде метаданных

    def filterCloudSentinel2 (self, img): 
        import ee
        quality = img.select('QA60').int()
        cloudBit = ee.Number(1024)
        cirrusBit = ee.Number(2048)
        cloudFree = quality.bitwiseAnd(cloudBit).eq(0)
        cirrusFree = quality.bitwiseAnd(cirrusBit).eq(0)
        clear = cloudFree.bitwiseAnd(cirrusFree)
        return img.updateMask(clear)

    def addLayer(self, date_start, image, visParams=None, name=None, shown=True, opacity=1.0):
        """
            Adds a given EE object to the map as a layer.
            https://developers.google.com/earth-engine/api_docs#map.addlayer
        """
        import ee
        if not isinstance(image, ee.Image) and not isinstance(image, ee.FeatureCollection) and not isinstance(image, ee.Feature) and not isinstance(image, ee.Geometry):
            err_str = "\n\nThe image argument in 'addLayer' function must be an instace of one of ee.Image, ee.Geometry, ee.Feature or ee.FeatureCollection."
            raise AttributeError(err_str)
        if isinstance(image, ee.Geometry) or isinstance(image, ee.Feature) or isinstance(image, ee.FeatureCollection):
            features = ee.FeatureCollection(image)
            color = '000000'
            if visParams and 'color' in visParams:
                color = visParams['color']
            image = features.style(**{'color': color})
        else:
            if isinstance(image, ee.Image) and visParams:
                image = image.visualize(**visParams)
        if name is None:
            # extract name from id
            try:
                name = json.loads(image.id().serialize())[
                    "scope"][0][1]["arguments"]["id"]
            except:
                name = "untitled"
        self.add_or_update_ee_image_layer(date_start, image, name, shown, opacity)

    def get_ee_image_url(self, image):
        import ee
        map_id = ee.data.getMapId({'image': image})
        url = map_id['tile_fetcher'].url_format
        return url

    def update_ee_layer_properties(self, date_start, layer, image, opacity):
        layer.setCustomProperty('ee-layer', True)
        if not (opacity is None):
            layer.renderer().setOpacity(opacity)
        layer.brightnessFilter().setContrast(25)
        layer.setAbstract('&datasetId=S2L1C&fromTime=%sT00%%3A00%%3A00.000Z&toTime=%sT23%%3A59%%3A59.999Z&layerId=6-SWIR'%(date_start,date_start))

        # serialize EE code
        ee_script = image.serialize()
        layer.setCustomProperty('ee-script', ee_script)

    def add_ee_image_layer(self, date_start, image, name, shown, opacity):
        url = "type=xyz&url=" + self.get_ee_image_url(image)
        layer = QgsRasterLayer(url, name, "wms")
        self.update_ee_layer_properties(date_start, layer, image, opacity)
        QgsProject.instance().addMapLayer(layer)
        root = QgsProject.instance().layerTreeRoot()
        #layer_list = root.checkedLayers()
        #idx = self._last_raster(layer_list)
        group = root.findGroup('S2SRC')
        if not group:
            group = root.insertGroup(0, 'S2SRC')
        #root.insertChildNode(0, QgsLayerTreeLayer(layer))
        group.insertChildNode(0, QgsLayerTreeLayer(layer))
        if not (shown is None):
            root.findLayer(layer.id()).setItemVisibilityChecked(shown)

    def update_ee_image_layer(self, date_start, image, layer, shown=True, opacity=1.0):
        url = "type=xyz&url=" + self.get_ee_image_url(image)
        layer.dataProvider().setDataSourceUri(url)
        layer.dataProvider().reloadData()
        self.update_ee_layer_properties(date_start, layer, image, opacity)
        layer.triggerRepaint()
        layer.reload()
        if not (shown is None):
            QgsProject.instance().layerTreeRoot().findLayer(
                layer.id()).setItemVisibilityChecked(shown)

    def get_layer_by_name(self, name):
        layers = QgsProject.instance().mapLayers().values()
        for l in layers:
            if l.name() == name:
                return l
        return None

    def _last_raster (self, lay_list):
        rasters = []
        for lay in lay_list:
            #if lay.dataProvider().name() == 'wms':
            if lay.type() == QgsMapLayerType.RasterLayer:
                rasters.append(lay)
        if len(rasters) > 0:
            idx = lay_list.index(rasters[0])
        else:
            idx = -2
        return idx

    def add_or_update_ee_image_layer(self, date_start, image, name, shown=True, opacity=1.0):
        layer = self.get_layer_by_name(name)
        if layer:
            if not layer.customProperty('ee-layer'):
                raise Exception('Layer is not an EE layer: ' + name)
            self.update_ee_image_layer(date_start, image, layer, shown, opacity)
        else:
            self.add_ee_image_layer(date_start, image, name, shown, opacity)

    def name(self):
        return 'Make a Sentinel-2 mosaic'

    def icon(self):
        return QIcon(os.path.dirname(__file__) + '/firehunter.png')

    def displayName(self):
        return self.name()

    def group(self):
        return self.groupId()

    def groupId(self):
        return ''

    def createInstance(self):
        return firehunterProcessingAlgorithm()