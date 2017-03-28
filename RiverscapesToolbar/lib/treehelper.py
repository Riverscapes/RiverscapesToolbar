from PyQt4.QtGui import QFont, QColor

def setFontColor(qtreeitem, colorstr):
    font = QFont()
    qtreeitem.set

def setFontBold(qtreeitem):
    font = QFont()
    font.setWeight(QFont.Bold)
    qtreeitem.setFont(0, font)

def setFontRegular(qtreeitem):
    font = QFont()
    font.setItalic(False)
    font.setWeight(QFont.Normal)
    qtreeitem.setFont(0, font)

def setFontItalic(qtreeitem):
    font = QFont()
    font.setItalic(True)
    qtreeitem.setFont(0, font)


def setItemIcon(qtreeitem, icon):
    # TODO: Need to figure out fonts
    print "coming soon"