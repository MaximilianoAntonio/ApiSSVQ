@description('The name of the User Assigned Managed Identity')
param name string

@description('The location where the identity will be deployed')
param location string

@description('Tags to be applied to the identity')
param tags object = {}

resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: name
  location: location
  tags: tags
}

output identityId string = userAssignedIdentity.id
output principalId string = userAssignedIdentity.properties.principalId
output clientId string = userAssignedIdentity.properties.clientId
