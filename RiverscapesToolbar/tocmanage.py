import os
import os.path

from qgis.utils import iface
from qgis.core import QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsMapLayerRegistry, QgsProject
from PyQt4.QtCore import Qt
from symbology.symbology import Symbology

# http://www.lutraconsulting.co.uk/blog/2014/07/25/qgis-layer-tree-api-part-2/

def AddGroup(sGroupName, parentGroup):
    
    # If no parent group specified then the parent is the ToC tree root
    if not parentGroup:
        parentGroup =  QgsProject.instance().layerTreeRoot()

    # Attempt to find the specified group in the parent
    thisGroup = parentGroup.findGroup(sGroupName)
    if not thisGroup:
        thisGroup = parentGroup.insertGroup(0, sGroupName)

    return thisGroup


def AddVectorLayer(theVector):
    # Loop over all the parent group layers for this raster
    # ensuring they are in the tree in correct, nested order
    parentGroup = None
    if len(theVector.data()) > 0:
        for aGroup in theVector.data()["group_layers"]:
            parentGroup = AddGroup(aGroup, parentGroup)

    assert parentGroup, "All rasters should be nested and so parentGroup should be instantiated by now"

    # Only add the layer if it's not already in the registry
    if not QgsMapLayerRegistry.instance().mapLayersByName(theVector.text()):
        rOutput = QgsVectorLayer(theVector.data()["filepath"].replace('\\', '/'), theVector.text(), "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(rOutput, False)
        parentGroup.addLayer(rOutput)

        legend = iface.legendInterface()
        legend.setLayerExpanded(rOutput, False)


    # if the layer already exists trigger a refresh
    else:
        print "REFRESH"
        QgsMapLayerRegistry.instance().mapLayersByName(theVector.text())[0].triggerRepaint()

def AddRasterLayer(theRaster):

    # Loop over all the parent group layers for this raster
    # ensuring they are in the tree in correct, nested order
    nodeData = theRaster.data(Qt.UserRole)
    symbology = nodeData.symbology
    filepath = nodeData.filepath

    parentGroup = None
    if len(filepath) > 0:
        for aGroup in getTreeAncestry(nodeData):
            parentGroup = AddGroup(aGroup, parentGroup)

    assert parentGroup, "All rasters should be nested and so parentGroup should be instantiated by now"

    # Only add the layer if it's not already in the registry
    if not QgsMapLayerRegistry.instance().mapLayersByName(nodeData.name):
        rOutput = QgsRasterLayer(filepath, nodeData.name)
        QgsMapLayerRegistry.instance().addMapLayer(rOutput, False)
        parentGroup.addLayer(rOutput)

        # Symbolize this layer
        Symbology().symbolize(rOutput, symbology)

    # if the layer already exists trigger a refresh
    else:
        print "REFRESH"
        QgsMapLayerRegistry.instance().mapLayersByName(nodeData.name)[0].triggerRepaint()

def getTreeAncestry(item):
    """
    Returns a really simple ancestry line so we can 
    build a map layer later
    :return: 
    """
    ancestry = []
    parent = item.rtParent
    while parent is not None:
        ancestry.append(parent.name)
        parent = parent.rtParent
    ancestry.reverse()
    return ancestry