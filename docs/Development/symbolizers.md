---
title: Layer Symbolizers
---

You can create symbolizers so that layers of a certain type are always symbolized the same way. There are mechanisms for both Raster and Vector symbolization.

All the code for symbolizing is in the [RiverscapesToolbar/RiverscapesToolbar/symbology](https://github.com/Riverscapes/RiverscapesToolbar/tree/master/RiverscapesToolbar/symbology) folder of the repo.

## Writing new symbolizers

The very quickest way to generate a new symbolizer is to find one that matches as closely as possible to what you want and then copy it:

There are demos for rasters (this list may be out of date):

* [raster_dem.py](https://github.com/Riverscapes/RiverscapesToolbar/blob/master/RiverscapesToolbar/symbology/symbolizers/raster_dem.py)
* [raster_dod.py](https://github.com/Riverscapes/RiverscapesToolbar/blob/master/RiverscapesToolbar/symbology/symbolizers/raster_dod.py)
* [raster_roughness.py](https://github.com/Riverscapes/RiverscapesToolbar/blob/master/RiverscapesToolbar/symbology/symbolizers/raster_roughness.py)
* [raster_slopedeg.py](https://github.com/Riverscapes/RiverscapesToolbar/blob/master/RiverscapesToolbar/symbology/symbolizers/raster_slopedeg.py)
* [raster_slopeper.py](https://github.com/Riverscapes/RiverscapesToolbar/blob/master/RiverscapesToolbar/symbology/symbolizers/raster_slopeper.py)

and here are the Vector ones. These are a lot rougher. Vector symbolization is much more nuanced than rasters.

* [vector_categorize.py](https://github.com/Riverscapes/RiverscapesToolbar/blob/master/RiverscapesToolbar/symbology/symbolizers/vector_categorize.py)
* [vector_graduated.py](https://github.com/Riverscapes/RiverscapesToolbar/blob/master/RiverscapesToolbar/symbology/symbolizers/vector_graduated.py)
* [vector_rulebased.py](https://github.com/Riverscapes/RiverscapesToolbar/blob/master/RiverscapesToolbar/symbology/symbolizers/vector_rulebased.py)
* [vector_single.py](https://github.com/Riverscapes/RiverscapesToolbar/blob/master/RiverscapesToolbar/symbology/symbolizers/vector_single.py)
* [vector_singlefill.py](https://github.com/Riverscapes/RiverscapesToolbar/blob/master/RiverscapesToolbar/symbology/symbolizers/vector_singlefill.py)

#### Sample Raster Symbolizer

``` python
from PyQt4.QtGui import QColor
from qgis.core import QgsColorRampShader

class RasterSymbolizer():

    symbology = "Roughness"

    def symbolize(self):
        self.colorramptype = QgsColorRampShader.DISCRETE
        # Now you have a self.layer object you can work with
        # self.opacity = 1.0

        self.colLst = [
            [0,QColor(194,82,60) , "Fines, Sand (0 to 2 mm)"],
            [2, QColor(240,180,17), "Fine Gravel (2 mm to 16 mm)"],
            [16, QColor(123,237,0), "Coarse Gravel (16 mm to 64 mm)"],
            [64, QColor(27,168,124), "Cobbles (64 mm to 256 mm)"],
            [256, QColor(11,44,122), "Boulders (> 256 mm)"],
        ]
```

#### Sample Vector Symbolizer:

``` python
from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsSingleSymbolRendererV2, QgsSimpleFillSymbolLayerV2

class VectorSymbolizer():

    symbology = "DEMO_singlefill"

    def symbolize(self):
        # create a new single symbol renderer
        symbol = QgsSymbolV2.defaultSymbol(self.layer.geometryType())
        self.renderer = QgsSingleSymbolRendererV2(symbol)

        # create a new simple marker symbol layer, a green circle with a black border
        properties = {'color': '#00FF00', 'color_border': '#000000'}
        symbol_layer = QgsSimpleFillSymbolLayerV2.create(properties)

        # assign the symbol layer to the symbol
        self.renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)
```

## Parts of the Symbolizer explained:

```python
from PyQt4.QtGui import QColor
from qgis.core import QgsSymbolV2, QgsSingleSymbolRendererV2, QgsSimpleFillSymbolLayerV2
```

Different kinds of symbolozation take different kinds of imports so you may need to customize this, especially for vectors

```python
class RasterSymbolizer():
## OR
class VectorSymbolizer():
```

Self-explanatory: what kind of symbolizer are you writing?

```python
symbology = "DEMO_singlefill"
```

This corresponds to the `symbology=""` attribute in your business logic XML file.

```python
    def symbolize(self):
```

here's where the actual symbolization starts. When a layer is loaded it will use this layer to set values for things like color ramps.

### What can I change inside `symbolize()`?

**For Rasters:**

* `self.opacity`: 0-1 opacity of this layer
* `self.colorramptype`:  `QgsColorRampShader.DISCRETE`, `EXACT`, `INTERPOLATED` 
* `self.colLst`: a list lists `[float(val), QColor(), str(labe)]`

**For Vectors:**

* For vectors you're trying to set the `self.renderer`

If this isn't feature-rich enough we can add functionality to `RasterSymbolizerPlugin` easily enough.

feel free to import modules like `math` to help you generate `self.colLst`

### What should I not do?

* Don't actually DO anything to the `layer` object if you can help it.
* Do NOT trigger a layer repaint. That's the responsibility of the `apply()` method

## Testing (Without the plugin)

You can test these symbolizers in QGIS without even using the RiverscapesToolbar plugin

1. Take everything in your `symbolize()` and remove all the `self.` references
2. Paste the modified contents of your `symbolize()` method as the filling in the following code sandwich.
3. You can paste this directly into QGIS' Python editor (open the python console and click on the "shw editor" button)
4. Click "Run Script"

``` python
# Fille in the name of your layer here
layer = QgsMapLayerRegistry.instance().mapLayersByName("Large Buffer")[0]

########### VVV This is the bit inside symbolize VVV """

symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
renderer = QgsSingleSymbolRendererV2(symbol)

# create a new simple marker symbol layer, a green circle with a black border
properties = {'color': '#FF0000', 'color_border': '#000000'}
symbol_layer = QgsSimpleFillSymbolLayerV2.create(properties)

# assign the symbol layer to the symbol
renderer.symbols()[0].changeSymbolLayer(0, symbol_layer)

########### ^^^ This is the bit inside symbolize ^^^

# assign the renderer to the layer
layer.setRendererV2(renderer)

# Finally trigger the repaint with the new style
layer.triggerRepaint()
```