from gcdxml import GCDXML
from PyQt4.QtGui import QTreeView, QApplication, QWidget
import sys

app = QApplication(sys.argv)
w = QWidget() 

# This file exists to test out the QTree view outside
# of QGIS
treeControl = QTreeView()
newGCD = GCDXML('/Users/matt/Desktop/gcd_project.gcd', treeControl)
print "DONE"
