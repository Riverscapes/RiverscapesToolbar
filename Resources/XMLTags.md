# XML

There are two XML files here and they have very different properties and lifecycles.

## 1. Tree XML

The tree XML defines how the tree looks for a given app. It is used to interpret the Project XML (see below) 

This file does not contain a version tag but instead references a URL which corresponds to a `schema.xsd` file which sits in a versioned folder.

Shipped and tied to the version of the software. Never shipped on its own. 

<http://releases.northarrowresearh.com/treeXML/1.0/schema.xsd> 


## 2. Project XML

This is the XML file that references actual files and data structures and their values (think `.gcd` files). 

When you see an XPath in the tree XML, chances are it is referencing the location of an object in the this XML file.

## XML Lifecycle 


## General Structure

### General Rules:

1. `<tree>` is the root. 
2. `<root>` and `<symbologies>` can be children of it.
3. There can be only one `<root>` inside tree.
4. `<root>` acts like `<node>` but it is special.

```xml
    <?xml version="1.0" encoding="utf-8"?>
    <tree>
        <root xpath="ProjectDS/Project">
            <label>GCD</label>
            <children collapsed="false">
                <node>
                    <label>Inputs</label>
                    <node>
                        ...
                    </node>
                </node>
            </children>
        </root>
        <symbologies>
            <symbology id="BlueToRed">
                ...
            </symbology>
        </symbologies>       
    </tree>
```

## Nodes

* `<label>`: `STRING` The label that will render in the tree.


### Entity

The entity is the "thing" the node represents. This will give information about how to render and orient the item.

* `<entity>`: `STRING` The type of thing this node represents (raster/vector) 
* `<project>`: `XPATH`
* `<data>`: `` Source
* `<symbology>`: `STRING`

Like so:

    <node>
        <label>Associated Surfaces</label>
        <type>ASS_SRF</type>
        <entity>
            <type>raster</type>
            <xpath>/ProjectDS/Project/DEMSurvey/AssociatedSurface</xpath>
            <data>Source</data>
            <label>Name</label>
            <symbology>BlueToRed</symbology>            
        </entity>
    </node>

## Symbologies

Symbologies are defined separately to make things more legible and be more portable. They are referenced by ID.

      <symbologies>
        <symbology id="BlueToRed">
          <ramp>
            <startcolour>blue</startcolour>
            <endcolour>red</endcolour>
            <type>stretch</type>
          </ramp>
        </symbology>
        <symbology id="RedToGreen">
          <ramp>
            <startcolour>red</startcolour>
            <endcolour>green</endcolour>
            <type>stretch</type>
          </ramp>
        </symbology>
      </symbologies>
