targetScope = 'resourceGroup'

metadata description = 'Creates Azure infrastructure for Gestor Vehiculos API'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

// App Service Plan parameters
@description('SKU for the App Service Plan')
param appServicePlanSku string = 'B1'

// Database parameters
@description('The administrator username for the PostgreSQL server')
param databaseAdministratorLogin string = 'pgadmin'

@description('The administrator password for the PostgreSQL server')
@secure()
param databaseAdministratorPassword string

@description('The name of the PostgreSQL database')
param databaseName string = 'gestordb'

// Application-specific parameters
@description('Django Secret Key')
@secure()
param djangoSecretKey string

@description('Django Debug mode')
param djangoDebug string = 'False'

@description('CORS allowed origins')
param corsAllowedOrigins string = '*'

// Tags that should be applied to all resources
var tags = {
  'azd-env-name': environmentName
  'app-name': 'gestor-vehiculos'
}

// Generate a unique token to be used in naming resources
var resourceToken = toLower(uniqueString(subscription().id, resourceGroup().id, environmentName))
var prefix = '${environmentName}-${resourceToken}'

// Create User Assigned Managed Identity first
module userIdentity 'modules/user-identity.bicep' = {
  name: 'user-identity'
  params: {
    name: 'mi-${prefix}'
    location: location
    tags: tags
  }
}

// Create modules for each service
module logAnalytics 'modules/log-analytics.bicep' = {
  name: 'log-analytics'
  params: {
    name: 'log-${prefix}'
    location: location
    tags: tags
  }
}

module appInsights 'modules/app-insights.bicep' = {
  name: 'app-insights'
  params: {
    name: 'appi-${prefix}'
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.workspaceId
  }
}

module keyVault 'modules/key-vault.bicep' = {
  name: 'key-vault'
  params: {
    name: 'kv-${resourceToken}'
    location: location
    tags: tags
    principalId: userIdentity.outputs.principalId
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    name: 'st${resourceToken}'
    location: location
    tags: tags
    principalId: userIdentity.outputs.principalId
  }
}

module database 'modules/database.bicep' = {
  name: 'database'
  params: {
    serverName: 'postgres-${resourceToken}'
    administratorLogin: databaseAdministratorLogin
    administratorPassword: databaseAdministratorPassword
    databaseName: databaseName
    location: location
    tags: tags
    keyVaultName: keyVault.outputs.keyVaultName
  }
}

module appServicePlan 'modules/app-service-plan.bicep' = {
  name: 'app-service-plan'
  params: {
    name: 'asp-${prefix}'
    location: location
    tags: tags
    sku: appServicePlanSku
  }
}

module webApp 'modules/web-app.bicep' = {
  name: 'web-app'
  params: {
    name: 'app-${prefix}'
    location: location
    tags: tags
    appServicePlanId: appServicePlan.outputs.appServicePlanId
    appInsightsConnectionString: appInsights.outputs.connectionString
    storageAccountName: storage.outputs.storageAccountName
    keyVaultName: keyVault.outputs.keyVaultName
    databaseConnectionSecretName: database.outputs.connectionStringSecretName
    userAssignedIdentityId: userIdentity.outputs.identityId
    djangoSecretKey: djangoSecretKey
    djangoDebug: djangoDebug
    corsAllowedOrigins: corsAllowedOrigins
  }
}

// App Service outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup().name
output RESOURCE_GROUP_ID string = resourceGroup().id

output APPLICATIONINSIGHTS_CONNECTION_STRING string = appInsights.outputs.connectionString
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.keyVaultUri
output AZURE_STORAGE_ACCOUNT_NAME string = storage.outputs.storageAccountName
output AZURE_STORAGE_CONTAINER_NAME string = storage.outputs.mediaContainerName

output SERVICE_GESTORVEHICULOS_IDENTITY_PRINCIPAL_ID string = userIdentity.outputs.principalId
output SERVICE_GESTORVEHICULOS_NAME string = webApp.outputs.name
output SERVICE_GESTORVEHICULOS_URI string = webApp.outputs.uri
