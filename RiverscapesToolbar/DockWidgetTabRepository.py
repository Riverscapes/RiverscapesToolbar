from lib.program import Program
from lib.s3.walkers import s3ProductWalker

def dlg_refresh(dlg, settings):
    """
    Refresh the main dialog
    :return:
    """
    print "clicked"
    program = Program(settings.getSetting("ProgramXMLUrl"))

    print 'Walking through and finding projects:'
    s3ProductWalker(program.Bucket)

    print "done"
# def _contextMenu(self, point):
#     """
#     Context Menu (right click on the treeWidget)
#     """
#
#     item = self.tree_widget.itemAt(point)
#     name_clicked = self._get_tag_from_item(item)
#
#     def add_tag():
#         dialog = QtGui.QInputDialog()
#         dialog.setTextValue(name_clicked)
#         if name_clicked != "":
#             proposition = name_clicked + '/'
#         else:
#             proposition = name_clicked
#         (tag, confirm) = dialog.getText(QtGui.QWidget(), \
#                                         "new tag", \
#                                         "enter tag name", \
#                                         0, \
#                                         proposition)
#         tag = str(tag)
#         if tag.endswith("/"):
#             raise ValueError("""tag should not end with /""")
#         if confirm and tag != "":
#             try:
#                 Tag.objects.get(name=tag)
#             except Tag.DoesNotExist:
#                 Tag.objects.create(name=tag)
#                 self.add_item(tag)
#                 self.select(tag)
#                 model_monitor.tag_added.emit()
#             else:
#                 box = QtGui.QMessageBox()
#                 box.setText("tag " + tag + " allready exists")
#                 box.exec_()
#
#     def remove_tag(dummy, name=name_clicked):
#         dial = QtGui.QMessageBox()
#         dial.setText("Delete tag '" + name + "': are you sure ?")
#         dial.setInformativeText("Tag will be removed from all referenced curves...")
#         dial.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
#         dial.setDefaultButton(QtGui.QMessageBox.Ok);
#         if dial.exec_():
#             tag = Tag.objects.get(name=name)
#             tag.delete()
#             model_monitor.tag_deletted.emit()
#             self.refresh()
#
#     def rename(dummy, name=name_clicked):
#         dialog = QtGui.QInputDialog()
#         dialog.setTextValue(name_clicked)
#         proposition = name_clicked
#         (tag, confirm) = dialog.getText(QtGui.QWidget(), \
#                                         "rename tag", \
#                                         "enter tag name", \
#                                         0, \
#                                         proposition)
#         if confirm:
#             new_name = str(tag)
#             tag = Tag.objects.get(name=name)
#             tag.name = new_name
#             tag.save()
#             self.refresh()
#
#     menu = QtGui.QMenu(self)
#     action_add_tag = QtGui.QAction("add tag...", self)
#     action_add_tag.triggered.connect(add_tag)
#     menu.addAction(action_add_tag)
#
#     action_rename_tag = QtGui.QAction("rename tag", self)
#     action_rename_tag.triggered.connect(rename)
#     menu.addAction(action_rename_tag)
#
#     action_remove_tag = QtGui.QAction("remove tag", self)
#     action_remove_tag.triggered.connect(remove_tag)
#     menu.addAction(action_remove_tag)
#
#     action_refresh_list = QtGui.QAction("refresh list", self)
#     action_refresh_list.triggered.connect(self.refresh)
#     menu.addAction(action_refresh_list)
#
#     self._exec_menu_at_right_place(menu, point)
