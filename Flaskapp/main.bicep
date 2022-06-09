// az login
// az account set --subscription

// az deployment group create --resource-group <Group name> --template-file <file name> 


var location = resourceGroup().location

param queueNames array = [
  'inputMike'
  'outputMike'
]

var queueName = 'mixitqueuemike'

// resource storageAccount 'Microsoft.Storage/storageAccounts@2021-08-01' = {
//   name: 'testmikestorage'
//   location: location
//   sku: {
//     name: 'Standard_LRS'
//   }
//   kind: 'StorageV2'
//   properties: {
//     accessTier: 'Hot'
//   }
// }

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'mixitappinsights'
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

resource appServicePlan 'Microsoft.Web/serverFarms@2021-03-01' = {
  name: 'testwebmike'
  location: location
  sku: {
    name: 'F1'
  }
}

resource appServiceApp 'Microsoft.Web/sites@2021-03-01' = {
  name: 'testmikeserviceplan'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
  }
}

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2021-11-01' = {
  location: location
  name: 'testmikeservicebus'
}
resource queues 'Microsoft.ServiceBus/namespaces/queues@2021-06-01-preview' = [for queueName in queueNames : {
  parent: serviceBusNamespace
  name: queueName
  // properties: {
  //   forwardDeadLetteredMessagesTo: queueName
  // }
}]
