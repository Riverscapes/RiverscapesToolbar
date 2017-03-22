#!/usr/bin/env bash

##############################################
# BE REALLY SURE YOU WANT TO RUN THIS
##############################################
# This file is used by Matt Reimer:
#
# When I debug I don't keep my source code in .qgis2/python/plugins
# I store it somewhere else and use pb_tool to deploy it to .qgis2/python/plugins
# That means when I debug, the breakpoint is hitting the .qgis2 version of the code
#
# If I make changes there I might want to copy those changes back so I can commit them
#
##############################################

QGSPATH=~/.qgis2/python/plugins/RiverscapesToolbar

cp $QGSPATH/*.py ../
cp -fr $QGSPATH/lib ../
