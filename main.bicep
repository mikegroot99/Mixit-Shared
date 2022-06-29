// az login
// az account set --subscription
// az deployment group create --resource-group <Group name> --template-file <file name> 

param queueNames array = [
  'inputOutlookqueuemike'
  'outputOutlookqueuemike'
  'inputsms'
]

param queueName string = 'mixithvaservicebusmike'
param location string = resourceGroup().location
param applicationInsightsName string = 'mixithvaappinsightsmike'
param applicationWebAppName string = 'MixitAppHvAMike'

resource appServicePlan 'Microsoft.Web/serverFarms@2021-03-01' = {
  name: 'testwebmixitmike'
  location: location
  sku: {
    name: 'F1'
  }
}

resource appServiceApp 'Microsoft.Web/sites@2021-03-01' = {
  name: applicationWebAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'Python|3.9'
    }
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    DisableIpMasking: false
    DisableLocalAuth: false
    Flow_Type: 'Bluefield'
    ForceCustomerStorageForProfiler: false
    ImmediatePurgeDataOn30Days: true
    IngestionMode: 'ApplicationInsights'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Disabled'
    Request_Source: 'rest'
  }
}

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2021-11-01' = {
  location: location
  name: queueName
}

resource queues 'Microsoft.ServiceBus/namespaces/queues@2021-06-01-preview' = [for queueName in queueNames : {
  parent: serviceBusNamespace
  name: queueName
}]

