@description('The name of the Log Analytics workspace')
param name string

@description('The location where the Log Analytics workspace will be deployed')
param location string

@description('Tags to be applied to the Log Analytics workspace')
param tags object = {}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

output workspaceId string = logAnalyticsWorkspace.id
output workspaceName string = logAnalyticsWorkspace.name
