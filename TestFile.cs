using EsriNL.Net.API;
using EsriNL.Net.API.Converters;
using EsriNL.Net.API.Data;
using EsriNL.Net.API.Extentions;
using InfographicAsAService.Requests;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using RestSharp;

namespace InfographicAsAService.QueueTrigger
{
    public static class ArcGisFeatureServerRequests
    {
        /// <summary>
        /// Gets the infographic Id to use when creating an infographic
        /// </summary>
        /// <param name="logger">The logger</param>
        /// <param name="surveyId">The id of the survey to get the active infographic id from</param>
        /// <returns>The id of the infographic to use</returns>
        public static string GetActiveInfographicId(ILogger logger, string surveyId)
        {

            // Get ActiveInfographicUrl param from Environment
            string activeInfographicUrl;
            try
            {
                activeInfographicUrl = EnvironmentManager.ActiveInfographicUrl;
            }
            catch (EnvironmentException ex)
            {
                return ReturnDefaultInfographic(ex.Message, logger);
            }

            string infographicIdField = EnvironmentManager.Infographic_id_field;


            // Start querying the feature layer
            QueryParameters queryParams = new()
            {
                Where = $"Survey_id = \'{surveyId}\'",
                OutFields = infographicIdField,
                ReturnGeometry = false
            };

            //The "1" is the layer to use and in this case is the surveys table where the surveys and their active infographic are stored
            FeatureLayer layer = new(ArcGisClient.Client, new Uri($"{activeInfographicUrl}/1"));
            FeaturesResponse? response = layer.Query(queryParams);

            // Check response
            if (response == null)
            {
                return ReturnDefaultInfographic("GetActiveInfographic response was null", logger);
            }

            Feature? ActiveInfographic = response.Features.FirstOrDefault();
            if (ActiveInfographic == null)
            {
                return ReturnDefaultInfographic("Something went wrong getting the infographic, no active infographic was found", logger);
            }

            ActiveInfographic.Attributes.TryGetValue(infographicIdField, out object? value);
            if (value != null)
            {
                return (string)value;
            }

            return ReturnDefaultInfographic("Field " + infographicIdField + " was not found", logger);
        }

        /// <summary>
        /// Returns the default infographic id, used when the feature layer request fails
        /// </summary>
        /// <param name="message">The warning message </param>
        /// <param name="logger"></param>
        /// <returns>The default infographic id</returns>
        private static string ReturnDefaultInfographic(string message, ILogger logger)
        {
            logger.LogWarning("{Message}, Getting default template id", message);
            string defaultInfographic = EnvironmentManager.DefaultInfographicId;
            return defaultInfographic;
        }

        /// <summary>
        /// Generic function for querying **public** feature layers
        /// </summary>
        /// <param name="queryParams">the params of the query</param>
        /// <param name="layerIndex">index of the layer to query</param>
        /// <param name="featureLayerUri">The Uri to the featurelayer to query</param>
        /// <param name="logger">the logger</param>
        /// <returns>The features response returned from the featurelayer</returns>
        public static FeaturesResponse? QueryFeatureLayer(QueryParameters queryParams, int layerIndex, Uri featureLayerUri, ILogger logger)
        {
            logger.LogInformation("Querying feature layer with uri: {Uri}", featureLayerUri.ToString());
            string relativeUri = $"{layerIndex}/Query";
            featureLayerUri = new Uri(featureLayerUri, relativeUri);

            RestRequest request = new(featureLayerUri);
            request.AddObjectToRequest(queryParams);
            request.AddParameter("f", "json");

            RestClient client = new();
            RestResponse response = client.Post(request);

            if (response?.Content == null)
            {
                logger.LogWarning("No features found with query: {Query}", queryParams.Where);
                return null;
            }

            return JsonConvert.DeserializeObject<FeaturesResponse>(response.Content, new GeometryConverter());
        }
    }

    public class ArcGisFeatureServerRequestException(string message) : Exception(message) { }
}
