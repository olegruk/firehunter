from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import Qgis, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsPointXY, QgsProject, QgsSettings
from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker

class CaptureCoord(QgsMapToolEmitPoint):

    captureStopped = pyqtSignal(float, float)

    def __init__(self, iface):
        QgsMapToolEmitPoint.__init__(self, iface.mapCanvas())
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.vertex = None

    def activate(self):
        self.canvas.setCursor(Qt.CrossCursor)
        self.snapcolor = QgsSettings().value( "/qgis/digitizing/snap_color" , QColor( Qt.magenta ) )

    def deactivate(self):
        self.removeVertexMarker()
        QgsMapToolEmitPoint.deactivate(self)

    def getCoord(self, pt):
        # Make sure the coordinate is transformed to EPSG:4326
        canvasCRS = self.canvas.mapSettings().destinationCrs()
        epsg4326 = QgsCoordinateReferenceSystem('EPSG:4326')
        if canvasCRS == epsg4326:
            pt4326 = pt
        else:
            transform = QgsCoordinateTransform(canvasCRS, epsg4326, QgsProject.instance())
            pt4326 = transform.transform(pt.x(), pt.y())
        lat = pt4326.y()
        lon = pt4326.x()
        return lat, lon

    def canvasMoveEvent(self, event):
        pt = self.snappoint(event.originalPixelPoint())
        lat, lon = self.getCoord(pt)
        self.iface.statusBarIface().showMessage("{} - {}".format(lat, lon), 4000)

    def snappoint(self, qpoint):
        match = self.canvas.snappingUtils().snapToMap(qpoint)
        if match.isValid():
            if self.vertex is None:
                self.vertex = QgsVertexMarker(self.canvas)
                self.vertex.setIconSize(12)
                self.vertex.setPenWidth(2)
                self.vertex.setColor(self.snapcolor)
                self.vertex.setIconType(QgsVertexMarker.ICON_BOX)
            self.vertex.setCenter(match.point())
            return (match.point())
        else:
            self.removeVertexMarker()
            return self.toMapCoordinates(qpoint)

    def canvasReleaseEvent(self, event):
        pt = self.snappoint(event.originalPixelPoint())
        self.removeVertexMarker()
        lat, lon = self.getCoord(pt)
        self.captureStopped.emit(lat, lon)

    def removeVertexMarker(self):
        if self.vertex is not None:
            self.canvas.scene().removeItem(self.vertex)
            self.vertex = None
