import os
import sys
from raster import RasterSymbolizerPlugin

class Symbology():
    _pluginpath = "plugins"
    _plugins = []
    _loaded = False

    def __init__(self):
        if not self._loaded:
            self.loadPlugins()

    def loadPlugins(self):
        """
        Load the symbology plugins
        :return: 
        """
        pluginpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), Symbology._pluginpath)
        sys.path.insert(0, pluginpath)

        # Loop over all our plugins and add them if we can
        for f in os.listdir(Symbology._pluginpath):
            fname, ext = os.path.splitext(f)
            if ext == '.py':
                mod = __import__(fname)
                Symbology._plugins.append(mod.Plugin)
        sys.path.pop(0)
        Symbology._loaded = True

    def symbolize(self, layer, type):
        """
        Here's where we choose the actual symbology
        """
        # TODO: implement raster/vector check on layer
        # Callback
        for plugin in Symbology.plugins:
            if plugin.NAME == type:
                return plugin(layer).apply()
        # Just choose the default
        return RasterSymbolizerPlugin(layer)







