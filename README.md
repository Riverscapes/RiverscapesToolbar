### Plugin Builder Results

Congratulations! You just built a plugin for QGIS!

Your plugin **AnalystToolbar** was created in:

```
/Users/matt/.qgis2/python/plugins/AnalystToolbar
```

Your QGIS plugin directory is located at:

```
/Users/matt/.qgis2/python/plugins
```

### What's Next

1. In your plugin directory, compile the resources file using pyrcc4 (simply run `make` if you have automake or use `pb_tool`)
2. Test the generated sources using **make test (or run tests from your IDE)
3. Copy the entire directory containing your new plugin to the QGIS plugin directory (see Notes below)
4. Test the plugin by enabling it in the QGIS plugin manager
5. Customize it by editing the implementation file `toolbar_viewer.py`
6. Create your own custom icon, replacing the default `icon.png`
7. Modify your user interface by opening `toolbar_dialog_base.ui` in Qt Designer

#### Notes:
* You can use the **Makefile to compile and deploy when you
        make changes. This requires GNU make (gmake). The Makefile is ready to use, however you 
        will have to edit it to add addional Python source files, dialogs, and translations.
* You can also use **pb_tool to compile and deploy your plugin. Tweak the pb_tool.cfg file included with your plugin as you add files. Install **`pb_tool` using `pip` or `easy_install` <http://loc8.cc/pb_tool>



### Developer setup

1. Clone this repo somewhere on your computer (not the `.qgis/python/plugins` folder. I'll explain)
2. run `pb_tool deploy` to copy this to your `.qgis2/python/plugins` folder
3. Add `~/.qgis2/python/plugins` to your soruce path in pyCharm so you can hit breakpoints

Why do we do this? 

### Developer Workflow

To develop a QGis plugin in a "correct" way you need to follow the steps:

1. **Code**: This is done in the source
2. **Deploy**: `pb_tool deploy` copies the source to the QGis folder as if you were the user.
3. **Debug**: Set breakpoints ... make changes. Mess around. 
4. **Back copy**: Copy any debug changes back into your source code.
5. **Commit**: to git. Now go back to step 1.