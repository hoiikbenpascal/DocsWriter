## **GetActiveInfographicId**
 Gets the infographic Id to use when creating an infographic
### Paramaters
|Name|Type|Description
|----|----|----|
|logger|ILogger|The logger|
|surveyId|string|The id of the survey to get the active infographic id from|
### Returns
`string` The id of the infographic to use


## **QueryFeatureLayer**
 Generic function for querying **public** feature layers
### Paramaters
|Name|Type|Description
|----|----|----|
|queryParams|QueryParameters|the params of the query|
|layerIndex|int|index of the layer to query|
|featureLayerUri|Uri|The Uri to the featurelayer to query|
|logger|ILogger|the logger|
### Returns
`FeaturesResponse?` The features response returned from the featurelayer


