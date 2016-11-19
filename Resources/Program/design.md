# Program XML

We need a way to represent the bucket file structure and hold that structure
programatically so that products can find their homes when they upload and also
so users can find the products they care about.

The following is meant to completely describe the ideas of the following document:
<https://docs.google.com/spreadsheets/d/1PBTDZ_R_fdjydQ8jXVQr1Uf5OCOrzXhkfu9wSvvliIQ/>

So according to this, you would be able to find the output of a fuzzy FHM product like so:
`/ColumbiaRiverBasin/JohnDay/Sites/CBW05583-028079/VISIT_1029/2012/Q_001/Analyses/Fuzzy/Steelhead/Spawner/Analysis1/fuzzyHSI.tif`

We do this using some basic building blocks:

* `<Container name="Network"> `: A container is a folder literally called what the name is "Network" in this case
* `<Level name="Watershed"> `: A level will have repeating elements. So instead of "Watershed" you'll have lots
     of folders, each wih the name of the Level (Watershed in this case) in question/
* `<Product>` : Products are the endpoint. If I can find a product then I can download or upload a whole project

```xml
<?xml version="1.0" encoding="utf-8"?>
<Program name="Riverscapes" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:noNamespaceSchemaLocation="XSD/V1/Program.xsd">
  <Container name="/">
    <Level name="Region">
      <Level name="Watershed">
          <Container name="Watershed">
            <Product name="GRTS Rollup" id="GRTS"/>
              <Product name="Context Layers" id="context"/>
          </Container>
          <Container name="Network">
            <Product name="BRAT Models" id="BRAT"/>
              <Product name="WRAT" id="WRAT"/>
              <Product name="Matt Imputation Crap" id="MIC"/>
              <Product name="GPP" id="GPP"/>
              <Product name="Capacity" id="capacity"/>
              <Product name="River Styles" id="RSTYLES"/>
          </Container>
          <Container name="Sites">
            <Level name="Site">
              <Level name="Visit">
                <Level name="Year">
                  <Level name="Flow">
                    <Product name="FHM" id="FHM"/>
                    <Product name="GUT" id="GUT"/>
                    <Product name="GCD" id="GCD"/>
                  </Level>
                  <Container name="Topography">
                    <Product name="DEM"/>
                  </Container>
                </Level>
              </Level>
            </Level>
            <Product name="FHM" id="FHM"/>
          </Container>
      </Level>
    </Level>
  </Container>
</Program>
```

