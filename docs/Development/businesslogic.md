---
title: Business logic XML
---

## Business logic XML

The purpose of the business logic XML is to translate `project.rs.xml` files into project trees with elements that can be added to a map.

``` xml
<?xml version="1.0" encoding="utf-8"?>
<Project xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="XSD/project_explorer.xsd">
  <Name>VBET</Name>
  <ProjectType>VBET</ProjectType>
  <Node xpathlabel="Name">
    <Children>
      <Repeater label="Realizations" xpath="Realizations/VBET">
        <!--This is a template for how each realization should render-->
        <Node xpathlabel="Name">
          <Children collapsed="false">
            <Node label="Inputs" xpath="Inputs">
              <Children>
                <Node label="Topography" xpath="Topography">
                  <Children>
                    <Node xpathlabel="Name" xpath="DEM" type="raster" symbology="DEM"/>
                    <Node xpathlabel="Name" xpath="Flow" type="raster" symbology="Flow"/>
                    <Node xpathlabel="Name" xpath="Slope" type="raster" symbology="SlopePer"/>
                  </Children>
                </Node>
                <Repeater label="Network Buffers" xpath="DrainageNetworks/Network/Buffers/Buffer">
                  <Node xpathlabel="Name" type="vector" symbology="DEMO_singlefill"/>
                </Repeater>
              </Children>
            </Node>
            <Node label="Analyses"/>
          </Children>
        </Node>
      </Repeater>
    </Children>
  </Node>
</Project>
```

By layering the various building blocks together you should be able t accomplish a wide variety of tree structures.

### `<Project>`

### `<Repeater>`

Repeaters can contain `<Node>` types. The `<Node>` inside a will be applied to each repeated element found inside that repeater's xpath results.

Repeaters have one attribute: `xpath` that you can use to specify the object that is repeated in the project xml.

### `<Children>`

Children can contain `<Node>` and `<Repeater>` types. They can only be used inside other `<Node>` tags.

They have one optional attribute: `collapsed="true/false"` which determines if this group is collapsed by default upon load.

### `<Node>`

#### Tags:

* `<TileService>`: (optional) If your node is a tile service (`type="tile"`) then put its url here
* `<Children>`: This node can have sub-nodes

#### Attributes:

Choose one of:
* `label`: The literal string you want to assign to this node as a label
* `xpathlabel`: if you don't use `label` and you want to look up your node label from the xml file you can do it this way

The following are optional:
* `type`: If you want your node to be added to the map you need to specify what its type is. See the "Node Data Types" section below for allowed values.
* `symbology`: If this is a map layer you can specify what symbology to use. This must match the `NAME` variable from the python symbology plugin in `RiverscapesToolbar/symbology/plugins/myplygin.py`
* `xpath`: Not to be confused with `xpathlabel`. This xpath sets the context for this node. Children nodes will inherit it.


### Node Data Types

Nodes can have different data types which affect how (if) the node loads into the map.

* `raster`: tif files
* `vector`: shp files
* `tile`: A url
* `file`: catch-all for any other kind of file. Right now this will just open up finder/explorer to this location.