# Writing new symbolization plugins

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

### `symbology`

* `symbology`: This corresponds to the `symbology=""` attribute in your business logic XML file.

## symbolize()

### What can I change?

* `self.opacity`: 0-1 opacity of this layer
* `self.colorramptype`:  `QgsColorRampShader.DISCRETE`, `EXACT`, `INTERPOLATED`
* `self.colLst`: a list lists `[float(val), QColor(), str(labe)]`

If this isn't feature-rich enough we can add functionality to `RasterSymbolizerPlugin` easily enough.

feel free to import modules like `math` to help you generate `self.colLst`

### What should I not do?

* Don't actually DO anything to the `layer` object if you can help it.
* Do NOT trigger a layer repaint. That's the responsibility of the `apply()` method