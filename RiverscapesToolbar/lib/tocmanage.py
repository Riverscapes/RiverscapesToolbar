import os
import os.path

from qgis.utils import iface
from qgis.core import QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsMapLayerRegistry, QgsProject

from RiverscapesToolbar.symbology.symbology import RasterSymbolizer

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
    parentGroup = None
    if len(theRaster.data()) > 0:
        for aGroup in theRaster.data()["group_layers"]:
            parentGroup = AddGroup(aGroup, parentGroup)

    assert parentGroup, "All rasters should be nested and so parentGroup should be instantiated by now"

    # Only add the layer if it's not already in the registry
    if not QgsMapLayerRegistry.instance().mapLayersByName(theRaster.text()):
        rOutput = QgsRasterLayer(theRaster.data()["filepath"], theRaster.text())
        QgsMapLayerRegistry.instance().addMapLayer(rOutput, False)
        parentGroup.addLayer(rOutput)
        
        # call Konrad's symbology method here using data()["symbology"]
        # DEBUG:: FILL IN THE PROPER TYPE
        RasterSymbolizer.symbolize(rOutput, 'DoD')

        if theRaster.data()["symbology"].lower() == "dem":
            demPath, demExtension = os.path.splitext( theRaster.data()["filepath"])
            hillshadePath = demPath + "HS" + demExtension
            
            if os.path.isfile(hillshadePath):
                rHillshade = QgsRasterLayer(hillshadePath, "Hillshade")
                QgsMapLayerRegistry.instance().addMapLayer(rHillshade, False)
                lHillshade = parentGroup.addLayer(rHillshade)
                legend = iface.legendInterface()
                legend.setLayerExpanded(rHillshade, False)

    # if the layer already exists trigger a refresh
    else:
        print "REFRESJH"
        QgsMapLayerRegistry.instance().mapLayersByName(theRaster.text())[0].triggerRepaint()