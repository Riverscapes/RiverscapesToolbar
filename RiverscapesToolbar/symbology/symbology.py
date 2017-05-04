import os
import sys
import raster

class Symbology():
    _pluginpath = "symbolizers"
    _plugins = []
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
        symbolizerInst = raster.RasterPlugin(layer)
        for plugin in Symbology._plugins:
            if plugin.NAME == type:
                # Monkey patch!
                symbolizerInst.SetSymbology = plugin.SetSymbology.__get__(symbolizerInst)
        # Just choose the default
        return symbolizerInst.apply()






