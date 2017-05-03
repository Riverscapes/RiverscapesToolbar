import os
import sys
import raster

class Symbology():
    _pluginpath = "plugins"
    _plugins = []
    _loaded = False

    def __init__(self):
        if not self._loaded:
            Symbology.loadPlugins()

    @staticmethod
    def loadPlugins():
        """
        Load the symbology plugins into a library. Use whatever we can find. 
        :return: 
        """
        pluginpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), Symbology._pluginpath)
        sys.path.insert(0, pluginpath)

        # Loop over all our plugins and add them if we can
        for f in os.listdir(pluginpath):
            fname, ext = os.path.splitext(f)
            if ext == '.py':
                mod = __import__(fname)
                if "Plugin" in mod.__dict__:
                    Symbology._plugins.append(mod.Plugin)
        sys.path.pop(0)
        Symbology._loaded = True

    @staticmethod
    def symbolize(layer, type):
        """
        Here's where we choose the actual symbology
        and apply to the layer
        """
        # TODO: implement raster/vector check on layer
        # Callback
        for plugin in Symbology.plugins:
            if plugin.NAME == type:
                # Monkey patch!
                symbolizerInst = raster.RasterPlugin(layer)
                symbolizerInst.SetSymbology = plugin.SetSymbology
                return symbolizerInst.apply()
        # Just choose the default
        return raster.RasterPlugin(layer)







