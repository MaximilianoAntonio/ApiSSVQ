@description('The name of the App Service')
param name string

@description('The location where the App Service will be deployed')
param location string

@description('Tags to be applied to the App Service')
param tags object = {}

@description('The resource ID of the App Service Plan')
param appServicePlanId string

@description('Application Insights connection string')
param appInsightsConnectionString string

@description('Storage account name')
param storageAccountName string

@description('Key Vault name')
param keyVaultName string

@description('Database connection string secret name')
param databaseConnectionSecretName string

@description('User Assigned Identity resource ID')
param userAssignedIdentityId string

@description('Django Secret Key')
@secure()
param djangoSecretKey string

@description('Django Debug mode')
param djangoDebug string = 'False'

@description('CORS allowed origins')
param corsAllowedOrigins string = '*'

var keyVaultUri = 'https://${keyVaultName}${environment().suffixes.keyvaultDns}/'

resource appService 'Microsoft.Web/sites@2024-04-01' = {
  name: name
  location: location
  tags: union(tags, {
    'azd-service-name': 'gestor-vehiculos-api'
  })
  kind: 'app,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlanId
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: true
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      scmMinTlsVersion: '1.2'
      http20Enabled: true
      healthCheckPath: '/health/'
      cors: {
        allowedOrigins: ['*']
        supportCredentials: false
      }
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'true'
        }
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'SECRET_KEY'
          value: djangoSecretKey
        }
        {
          name: 'DEBUG'
          value: djangoDebug
        }
        {
          name: 'ALLOWED_HOSTS'
          value: '${name}.azurewebsites.net,localhost,127.0.0.1'
        }
        {
          name: 'DATABASE_URL'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=${databaseConnectionSecretName})'
        }
        {
          name: 'DB_HOST'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=database-host)'
        }
        {
          name: 'DB_NAME'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=database-name)'
        }
        {
          name: 'DB_USER'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=database-user)'
        }
        {
          name: 'DB_PASSWORD'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=database-password)'
        }
        {
          name: 'DB_PORT'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=database-port)'
        }
        {
          name: 'AZURE_STORAGE_ACCOUNT_NAME'
          value: storageAccountName
        }
        {
          name: 'AZURE_STORAGE_CONTAINER_NAME'
          value: 'media'
        }
        {
          name: 'CORS_ALLOWED_ORIGINS'
          value: corsAllowedOrigins
        }
        {
          name: 'FORCE_HTTPS'
          value: 'true'
        }
        {
          name: 'SECURE_SSL_REDIRECT'
          value: 'true'
        }
        {
          name: 'USE_X_FORWARDED_HOST'
          value: 'true'
        }
        {
          name: 'USE_X_FORWARDED_PORT'
          value: 'true'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
        {
          name: 'AZURE_KEY_VAULT_ENDPOINT'
          value: keyVaultUri
        }
      ]
    }
  }
}

// Add Site Extension for better Python performance
resource pythonSiteExtension 'Microsoft.Web/sites/siteextensions@2024-04-01' = {
  name: 'python311x64'
  parent: appService
}

output appServiceId string = appService.id
output name string = appService.name
output uri string = 'https://${appService.properties.defaultHostName}'
output userAssignedIdentityId string = userAssignedIdentityId
