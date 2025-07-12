@description('The name of the PostgreSQL server')
param serverName string

@description('The administrator username for the PostgreSQL server')
param administratorLogin string

@description('The administrator password for the PostgreSQL server')
@secure()
param administratorPassword string

@description('The name of the database')
param databaseName string

@description('The location where the PostgreSQL server will be deployed')
param location string

@description('Tags to be applied to the PostgreSQL server')
param tags object = {}

@description('The name of the Key Vault to store connection string')
param keyVaultName string

resource postgresqlServer 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: serverName
  location: location
  tags: tags
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    version: '16'
    storage: {
      storageSizeGB: 32
      autoGrow: 'Enabled'
      type: 'Premium_LRS'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    authConfig: {
      activeDirectoryAuth: 'Disabled'
      passwordAuth: 'Enabled'
    }
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  name: databaseName
  parent: postgresqlServer
  properties: {
    charset: 'UTF8'
    collation: 'en_US.UTF8'
  }
}

// Create firewall rule to allow Azure services
resource firewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  name: 'AllowAzureServices'
  parent: postgresqlServer
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Reference to existing Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

// Store database connection string in Key Vault
resource databaseConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'database-connection-string'
  parent: keyVault
  properties: {
    value: 'postgresql://${administratorLogin}:${administratorPassword}@${postgresqlServer.properties.fullyQualifiedDomainName}:5432/${databaseName}?sslmode=require'
  }
}

// Store individual database connection components
resource dbHostSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'database-host'
  parent: keyVault
  properties: {
    value: postgresqlServer.properties.fullyQualifiedDomainName
  }
}

resource dbNameSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'database-name'
  parent: keyVault
  properties: {
    value: databaseName
  }
}

resource dbUserSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'database-user'
  parent: keyVault
  properties: {
    value: administratorLogin
  }
}

resource dbPasswordSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'database-password'
  parent: keyVault
  properties: {
    value: administratorPassword
  }
}

resource dbPortSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'database-port'
  parent: keyVault
  properties: {
    value: '5432'
  }
}

output serverId string = postgresqlServer.id
output serverName string = postgresqlServer.name
output fullyQualifiedDomainName string = postgresqlServer.properties.fullyQualifiedDomainName
output connectionStringSecretName string = databaseConnectionStringSecret.name
