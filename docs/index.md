---
title: Home
weight: 1
---

The Riverscapes Viewer is a QGis plugin you can use to interact with riverscapes data

Using this tool you can:

* Browse the Riverscapes data repository
* Download / Upload Riverscapes projects
* View Riverscapes project data using the QGIS map viewer.

The Riverscapes Viewer has its own documentation so please go there 

### Some topics to get you started: 

1. [Quick Start Guide](quickstart.html)
2. [Anatomy of the plugin](anatomy.html)

### Development

There are currently two things that model owners can contribute to the Riverscapes project to help their projects be visible and usable in the Riverscapes Viewer.

* **[Symbolizing layers](Development/symbolizers.html)**: Create symbolizers so that layers of a certain type are always symbolized the same way. There are mechanisms for both Raster and Vector symbolization.
* **[Project Parsers](Development/businesslogic.html)**: This is a single XML file that decides how the `project.rs.xml` gets parsed by QGIS' layer manager. 