---
title: Adding Tile Layers to QGIS
---

# Adding Tile Layers to QGIS

There are numerous tile layers available online that make for useful context when perusing the data warehouse. We are working on integrating them into the Riverscapes Toolbar (RAVE) but for now here are some instructions on how to load them into QGIS:

## Requirements

* QGIS 2.18.0 or newer
* Internet connection

## Instructions

1. Load QGIS

2. Right click in the QGIS toolbar area and open the **Browser Panel**

   ![browser panel]({{site.baseurl}}/assets/images/browser_panel.png)

3. Right click on the **Tile Server (XYZ)** and choose **New Connection...**

4. Enter the URL of the desired tile server (see below for both a list of useful tile servers and also some gotchas)

   ![tile server]({{site.baseurl}}/assets/images/tile_server_url.png)

5. Click OK to save the tile service. It should appear listed under the Tile Server node in the Browser Panel tree.

6. Drag the tile service from the Browser Panel into the QGIS table of contents and it should appear in the map.

## Common Tile Services

| Name                    | URL                                      |
| ----------------------- | ---------------------------------------- |
| Open Street Map         | `http://tile.openstreetmap.org/{z}/{x}/{y}.png` |
| Google Hybrid           | `https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}` |
| Google Road             | `https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}` |
| Hillshade               | `http://c.tiles.wmflabs.org/hillshading/{z}/{x}/{y}.png` |
| OSM France              | `http://osm25.openstreetmap.fr/osmfr/{z}/{x}/{y}.png` |
| Thunderforest Landscape | `https://tile.thunderforest.com/landscape/{z}/{x}/{y}.png` |
| Thunderforest Outdoors  | `https://tile.thunderforest.com/outdoors/{z}/{x}/{y}.png` |


## Troubleshooting

* If you're copy and pasting the tile service URL be careful with UTF-8 character encoding. The curly braces might not copy properly and you might need to use the cursor and re-type them manually.