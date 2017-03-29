from PyQt4.QtGui import QFont, QColor, QBrush

def setFontColor(qtreeitem, colorhex):
    qtreeitem.setForeground(QBrush(QColor(colorhex)))

def setFontBold(qtreeitem):
    font = QFont()
    font.setWeight(QFont.Bold)
    qtreeitem.setFont(font)

def setFontRegular(qtreeitem):
    font = QFont()
    font.setItalic(False)
    font.setWeight(QFont.Normal)
    qtreeitem.setFont(font)

def setFontItalic(qtreeitem):
    font = QFont()
    font.setItalic(True)
    qtreeitem.setFont(font)


def setItemIcon(qtreeitem, icon):
    # TODO: Need to figure out fonts
    print "coming soon"