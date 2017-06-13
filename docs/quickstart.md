---
title: Quick Start
weight: 2
---

Installing the RAVE plugin is relatively straightforward, but for it to work properly and communicate with the riverscapes project repository you will need to install the Amazon Web Services ([AWS](https://aws.amazon.com)) Command Line Interface ([CLI](https://aws.amazon.com/cli/)) and the [boto3](https://boto3.readthedocs.io/en/latest/) library for pip.

If you installed the plugin first you do not need to uninstall it. Just complete the steps you didn't already do below. There is also no harm in re-doing any of these steps.

We are working to streamline and remove as many of these steps as we can but for now here are the instructions.

## Step 1: Install AWS CLI (Amazon Web Services Command-Line Interface)

Installing the AWS CLI will allow you to set up your AWS credentials in the system in a place where the RAVE plugin can find them:

1. Follow the online instructions for [installing the AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)
2. Open a command prompt and type `aws configure`
3. Type your credentials as given to you. Contact North Arrow Research (email info [`aT`] northarrowresearch.com) if you need keys.

## Step 2: Install `boto3`

Boto3 is the library that allows QGIS to communicate with AWS using python.

1. Navigate to `c:\OSGEO4W64` (if that is where you isntalled QGIS) and double-click `OSGeo4W.bat`. This will give you a command shell with all appropriate python libraries and environment variables set.
2. type `easy_install pip` to install the python package manager (this may already have been done but no harm in doing it again).
3. type `pip install boto3` 

If all goes well you should have boto3 installed. Test it out by running the `python` command in your shell and try to import boto3. If it imports without any errors you're good:

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

1. Add the [NAR web store](http://riverscapes.northarrowresearch.com/plugins.xml) to your QGIS web stores. 
2. You should then see `Riverscapes Toolbar` as an option. You can click "Install Plugin" button from there. 

***NB: Currently there is a bug where plugins from the NAR are not found after clicking the install button. Closing and re-opening QGIS fixes this problem.***

Once you have enabled the plugin you will see a blue "R" icon in the toolbar area of QGIS. ![icon](/images/toolbar_icon.png)

----------

## First time Setup

If this is your first time using the RAVE toolbar you'll need to click the **settings** button and make sure it's pointing to a valid XML file for the remote and a valid, existing folder for the local data.