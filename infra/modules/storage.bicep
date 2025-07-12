@description('The name of the storage account')
param name string

@description('The location where the storage account will be deployed')
param location string

@description('Tags to be applied to the storage account')
param tags object = {}

@description('Principal ID of the managed identity that will have access to storage')
param principalId string

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    accessTier: 'Hot'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

// Create container for media files
resource mediaContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storageAccount.name}/default/media'
  properties: {
    publicAccess: 'None'
  }
}

// Grant the managed identity Storage Blob Data Contributor role
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(storageAccount.id, principalId, 'Storage Blob Data Contributor')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name
output mediaContainerName string = 'media'
output primaryEndpoints object = storageAccount.properties.primaryEndpoints
