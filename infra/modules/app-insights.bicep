@description('The name of the Application Insights resource')
param name string

@description('The location where the Application Insights resource will be deployed')
param location string

@description('Tags to be applied to the Application Insights resource')
param tags object = {}

@description('The resource ID of the Log Analytics workspace')
param logAnalyticsWorkspaceId string

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspaceId
  }
}

output applicationInsightsId string = applicationInsights.id
output instrumentationKey string = applicationInsights.properties.InstrumentationKey
output connectionString string = applicationInsights.properties.ConnectionString
