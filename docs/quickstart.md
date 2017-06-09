---
title: Quick Start
weight: 2
---

Installing the Riverscapes Toolbar plugin is relatively straightforward but for it to work properly and commicate with AWS you will need to install the AWS CLI and the boto3 library for pip.

If you installed the plugin first you do not need to uninstall it. Just complete the steps you didn't already do below. There is also no harm in re-doing any of these steps.

We are working to streamline and remove as many of these steps as we can but for now here are the instructions.

## Step 1: Install AWS CLI (Amazon Web Services Command-Line Interface)

Installing the AWS CLI will allow you to set up your AWS credentials in the system in a place where the riverscapes toolbar can find them

1. Follow the instructions from the website to install the AWS CLI
2. Open a command prompt and type `aws configure`
3. Type your credentials as given to you. Contact North Arrow Research if you need keys.

## Step 2: Install `boto3`

Boto3 is the library that allows QGIS to communicate with AWS using python.

1. Navigate to c:\OSGEO4W and double click NEED FILENAMEthe batch file. 
2. type `easy_install pip` to install the python package manager
3. type `pip install boto3` 

## Step 3: Install the plugin from the NAR web store

1. Add the NAR web store to your QGIS web stores. 
2. You should then see `Riverscapes Toolbar` as an option. You can click "Install Plugin" button from here. 

***NB: Currently there is a bug where plugins from the NAR are not found after clicking the install button. Closing and re-opening QGIS fixes this problem.***

----------

## First time Setup

If this is your first time in the product you'll need to click the **settings** button and made sure it's pointing to a valid XML file for the remote and a valid, existing folder for the local data.