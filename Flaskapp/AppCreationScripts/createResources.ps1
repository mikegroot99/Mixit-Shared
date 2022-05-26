$rg = 'Mixit2-rg'

Select-AzSubscription -SubscriptionId '7421d281-52e1-4c64-b11d-12ee02151732'
#New-AzResourceGroup -Name $rg -Location westeurope -Force

New-AzResourceGroupDeployment `
    -Name 'newservicebusmixit' `
    -ResourceGroupName $rg `
    -TemplateFile 'resources/01_servicebus.json'

New-AzResourceGroupDeployment `
    -Name 'newfunctionappmixit' `
    -ResourceGroupName $rg `
    -TemplateFile 'resources/02_functionApp.json'

New-AzResourceGroupDeployment `
    -Name 'newwebappmixit' `
    -ResourceGroupName $rg `
    -TemplateFile 'resources/03_webApp.json'