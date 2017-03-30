from PyQt4.QtGui import QFont, QColor, QBrush

def setFontColor(qtreeitem, colorhex, column=None):
    if column is not None:
        qtreeitem.setForeground(column, QBrush(QColor(colorhex)))
    else:
        qtreeitem.setForeground(QBrush(QColor(colorhex)))



def setFontBold(qtreeitem, column=None):
    font = QFont()
    font.setWeight(QFont.Bold)
    if column is not None:
        qtreeitem.setFont(column, font)
    else:
        qtreeitem.setFont(font)

def setFontRegular(qtreeitem, column=None):
    font = QFont()
    font.setItalic(False)
    font.setWeight(QFont.Normal)
    if column is not None:
        qtreeitem.setFont(column, font)
    else:
        qtreeitem.setFont(font)

def setFontItalic(qtreeitem, column=None):
    font = QFont()
    font.setItalic(True)
    if column is not None:
        qtreeitem.setFont(column, font)
    else:
        qtreeitem.setFont(font)


def setItemIcon(qtreeitem, icon):
    # TODO: Need to figure out fonts
    print "coming soon"