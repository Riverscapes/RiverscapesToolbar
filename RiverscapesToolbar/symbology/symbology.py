import os
import sys
from raster import RasterPlugin
from vector import VectorPlugin
from qgis.core import QgsRasterLayer, QgsVectorLayer

class Symbology():

    _pluginpath = "symbolizers"

    class _plugins:
        vector=[]
        raster=[]

    _loaded = False

    def __init__(self):
        if not self._loaded:
            Symbology.loadPlugins()

    @staticmethod
    def loadPlugins():
        """
        Load the symbology symbolizers into a library. Use whatever we can find. 
        :return: 
        """
        pluginpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), Symbology._pluginpath)
        sys.path.insert(0, pluginpath)

        # Loop over all our symbolizers and add them if we can
        for f in os.listdir(pluginpath):
            fname, ext = os.path.splitext(f)
            if ext == '.py':
                mod = __import__(fname)
                if "RasterSymbolizer" in mod.__dict__:
                    Symbology._plugins.raster.append(mod.RasterSymbolizer)
                if "VectorSymbolizer" in mod.__dict__:
                    Symbology._plugins.vector.append(mod.VectorSymbolizer)
        sys.path.pop(0)
        Symbology._loaded = True

    @staticmethod
    def symbolize(layer, symbology):
        """
        Here's where we choose the actual symbology
        and apply to the layer
        """
        # TODO: implement raster/vector check on layer
        # Callback

        if type(layer) is QgsRasterLayer:
            symbolizerInst = RasterPlugin(layer)
            for plugin in Symbology._plugins.raster:
                if plugin.symbology == symbology:
                    # Monkey patch!
                    symbolizerInst.symbolize = plugin.symbolize.__get__(symbolizerInst)

        elif type(layer) is QgsVectorLayer:
            symbolizerInst = VectorPlugin(layer)
            for plugin in Symbology._plugins.vector:
                if plugin.symbology == symbology:
                    # Monkey patch!
                    symbolizerInst.symbolize = plugin.symbolize.__get__(symbolizerInst)

        # Just choose the default
        return symbolizerInst.apply()






