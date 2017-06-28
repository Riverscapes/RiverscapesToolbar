---
title: Quick Start
weight: 2
---

Installing the RAVE plugin itself is relatively straightforward. It's a simple QGIS plugin. However, RAVE communicates with an online data warehouse of model products. This data warehouse is stored on Amazon's Web Services (AWS) and so you need to also install several tools that enable RAVE to communicate with Amazon's storage systems. We are working to streamline and remove as many of these steps as we can but for now here are the instructions.

If you installed the plugin first you do not need to uninstall it. Just complete the steps you didn't already do below. There is also no harm in re-doing any of these steps.

Some of the steps below differ if you are running the standalone version of QGIS versus the developer version. ***How do I know if I have the developer or standalone version of QGIS installed?*** Generally if you see in your `c:\` drive a folder called `c:\OSGEO4W64` then you have the developer version of QGIS installed and should follow those instructions (below).

## Step 1: Install AWS CLI

Installing the AWS command line interface (CLI) will allow you to set up your AWS credentials in the system in a place where the RAVE plugin can find them:

1. Follow the online instructions for [installing the AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)
2. Open a command prompt and type `aws configure`
3. Type your credentials as given to you. Contact North Arrow Research (email info [`aT`] northarrowresearch.com) if you need keys.

## Step 2: Install `boto3`

Boto3 is the library that allows QGIS to communicate with AWS using python. It essentially sits between the AWS CLI and RAVE.

**QGIS Standalone Users:**

1. Click `Start` button and type `OSGEO4W` (yes, even in the standalone version)
2. You should see program called "OSGEO4W Shell". Click that and you should get a DOS command window in which you should type the following:

```
python -m pip install boto3 --user
```



**QGIS OSGEO4W64 (developer) Users:**

1. Navigate to `c:\OSGEO4W64` (if that is where you installed QGIS) and double-click `OSGeo4W.bat`. This will give you a command shell with all appropriate python libraries and environment variables set.
2. type `easy_install pip` to install the python package manager (this may already have been done but no harm in doing it again).
3. type `pip install boto3` 

If all goes well you should have boto3 installed. Test it out by typing the command `python` in your shell and then `import boto3`. If it imports without any errors you're good:

```
GDAL 2.2.0, released 2017/04/28

C:\OSGeo4W64>python
Python 2.7.5 (default, May 15 2013, 22:44:16) [MSC v.1500 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import boto3
>>>
```

here's what it looks like when it **doesn't** work:

```bash
GDAL 2.2.0, released 2017/04/28

C:\OSGeo4W64>python
Python 2.7.5 (default, May 15 2013, 22:44:16) [MSC v.1500 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import boto3
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: No module named boto3
>>>
```


## Step 3: Install the plugin from the NAR web store

1. Start QGIS
2. On the `Plugins` menu, click `Manage and Install Plugins...`
3. Switch to the `Settings` tab
4. Click `Add...` in the bottom right.
5. Enter a name for this new pugin store, e.g. `NAR Plugins` 
6. Paste the URL to the [NAR web store](http://riverscapes.northarrowresearch.com/plugins.xml)
7. Click  `OK`
8. You should then see `Riverscapes Toolbar` as an option. You can click "Install Plugin" button from there. 

![Plugin installation](/images/plugin_management.png)

Once you have enabled the plugin you will see a blue "R" icon in the toolbar area of QGIS. ![icon]({{site_url}}/images/toolbar_icon.png) Click this R button to open the RAVE dockable window.

----------

## First time Setup

If this is your first time using the RAVE toolbar you'll need to click the **settings** button and make sure it's pointing to a valid XML file for the remote and a valid, existing folder for the local data.