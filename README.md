### Plugin Builder Results

Congratulations! You just built a plugin for QGIS!<br/><br />

<div id='help' style='font-size:.9em;'>
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
1. Test the generated sources using **make test (or run tests from your IDE)
1. Copy the entire directory containing your new plugin to the QGIS plugin directory (see Notes below)
1. Test the plugin by enabling it in the QGIS plugin manager
1. Customize it by editing the implementation file `toolbar_viewer.py`
1. Create your own custom icon, replacing the default `icon.png`
1. Modify your user interface by opening `toolbar_dialog_base.ui` in Qt Designer

#### Notes:
<ul>
* You can use the **Makefile to compile and deploy when you
        make changes. This requires GNU make (gmake). The Makefile is ready to use, however you 
        will have to edit it to add addional Python source files, dialogs, and translations.
* You can also use **pb_tool to compile and deploy your plugin. Tweak the <i>pb_tool.cfg file included with your plugin as you add files. Install **pb_tool using 
        <i>pip or <i>easy_install. See <a href="http://loc8.cc/pb_tool">http://loc8.cc/pb_tool for more information.



