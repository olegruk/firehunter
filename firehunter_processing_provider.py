# -*- coding: utf-8 -*-

"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider
from .firehunter_processing_algorithm import firehunterProcessingAlgorithm
import os.path

class firehunterProcessingProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        pass

    def loadAlgorithms(self):
        self.addAlgorithm(firehunterProcessingAlgorithm())

    def id(self):
        return 'Fire hunter'

    def name(self):
        return 'Fire hunter'

    def icon(self):
        return QIcon(os.path.dirname(__file__) + '/firehunter.png')

    def longName(self):
        return self.name()
