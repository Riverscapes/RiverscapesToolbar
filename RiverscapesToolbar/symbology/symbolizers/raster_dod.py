from PyQt4.QtGui import QColor
from qgis.core import QgsColorRampShader
import math

class Plugin():

    NAME="DoD"

    def SetSymbology(self):
        self.colorramptype = QgsColorRampShader.DISCRETE

        nClasses = 20
        lo = self.stats.minimumValue
        hi = self.stats.maximumValue

        if abs(lo) > abs(hi):
            hi = abs(lo)
        else:
            lo = hi*-1.0

        rng = hi*2.0
        interval = rng/(nClasses*1.0)

        # Custom function
        nRound = magnitude(rng)

        if nRound < 0:
            nRound = abs(nRound) + 2

        else:
            nRound = 2

        valLst = [ lo ]
        labLst = []

        for i in range(1,nClasses+1,1):
            valLst.append(lo + i*interval)
            labLst.append(str(round(valLst[i-1], nRound))+" to "+str(round(valLst[i], nRound)))

        self.colLst = [
            [valLst[0], QColor(230, 0, 0), labLst[0]],
            [valLst[1], QColor(235, 45, 23), labLst[1]],
            [valLst[2], QColor(240, 67, 41), labLst[2]],
            [valLst[3], QColor(242, 88, 61), labLst[3]],
            [valLst[4], QColor(245, 108, 81), labLst[4]],
            [valLst[5], QColor(245, 131, 105), labLst[5]],
            [valLst[6], QColor(245, 151, 130), labLst[6]],
            [valLst[7], QColor(242, 171, 155), labLst[7]],
            [valLst[8], QColor(237, 190, 180), labLst[8]],
            [valLst[9], QColor(230, 208, 207), labLst[9]],
            [valLst[10], QColor(218, 218, 224), labLst[10]],
            [valLst[11], QColor(197, 201, 219), labLst[11]],
            [valLst[12], QColor(176, 183, 214), labLst[12]],
            [valLst[13], QColor(155, 166, 207), labLst[13]],
            [valLst[14], QColor(135, 150, 201), labLst[14]],
            [valLst[15], QColor(110, 131, 194), labLst[15]],
            [valLst[16], QColor(92, 118, 189), labLst[16]],
            [valLst[17], QColor(72, 105, 184), labLst[17]],
            [valLst[18], QColor(49, 91, 176), labLst[18]],
            [valLst[19], QColor(2, 7, 168), labLst[19]],
        ]


def magnitude(x):
    return int(math.floor(math.log10(x)))