#!/bin/bash

NEWVERSION=$1

sed -i -- "s/^version=.*/version=${NEWVERSION}/g" metadata.txt
git checkout master
git add metadata.txt;
git commit -m "Upgrading to version: $NEWVERSION"
git tag $NEWVERSION
git push --all
pb_tool zip
aws s3 cp RiverscapesToolbar.zip s3://qgis.northarrowresearch.com/plugins/riverscapestoolbar/riverscapestoolbar-$NEWVERSION.zip --profile matt
