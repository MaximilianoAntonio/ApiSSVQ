@description('The name of the App Service Plan')
param name string

@description('The location where the App Service Plan will be deployed')
param location string

@description('Tags to be applied to the App Service Plan')
param tags object = {}

@description('The SKU for the App Service Plan')
param sku string = 'B1'

resource appServicePlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    reserved: true // Linux
  }
  kind: 'linux'
}

output appServicePlanId string = appServicePlan.id
output appServicePlanName string = appServicePlan.name
