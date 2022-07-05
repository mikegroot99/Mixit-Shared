# Dit is Project Personal Assistent - Mixit

**Beschrijving:** \
Deze readme bevat informatie over het opzetten van deze repository naar een Azure DevOps omgeving.

## Uitleg applicatie
- Map FunctionApps: Hierin staat de code van de Function App. Deze moet handmatig overgezet worden naar de applicatie in de Azure Portal na het aanmaken van de resources.
- .github: Hierin staat de pipeline. Deze wordt automatisch actief wanneer de publish profile gekoppeld is. Die stap is hieronder te vinden.

De stappen die doorlopen moet worden:

### Koppel applicatie naar uw eigen Git omgeving

1. Clone deze repository naar een lokale omgeving.
1. Installeer de Azure extentie voor VS Code.
1. Maak een nieuwe repository aan in Github.
1. Push vervolgens de repository naar uw eigen Git omgeving.

### Resources aanmaken in Azure
De Pipeline is op dit moment nog niet gekoppeld aan uw Azure omgeving. Hiervoor moeten eerst de resources aangemaakt worden in Azure, daarna moet een secret key (geheime sleutel) worden opgehaald in Azure om deze veilig te verbinden met uw Github Repository.

1. Log in bij Azure via de Terminal via Visual Studio code, zorg dat u de gedownloadde repository open hebt staan.
1. Voer het `main.bicep` bestand uit met het volgende commando: `az deployment group create --resource-group <resource-group-name> --template-file main.bicep `
 \ Uitleg parameters:
2. Controlleer of de resources zijn aangemaakt door in te loggen in de portal van Azure.

### Secret Key toevoegen aan repository
Om een connectie te maken vanuit Github naar Azure is een publish profile nodig. Deze kan worden aangemaakt met de volgende stappen:

1. Log in bij de Azure Portal.
1. Ga bij de Resource groep naar de App Service die is aangemaakt.
1. Klik op `get publish profile` in de menubalk bovenin voor het ophalen van de publish profile. Deze wordt vervolgens gedownload.
1. Log in bij Github, ga vervolgens naar de instellingen van de Github Repository -> Secret Keys en maak een nieuwe aan. Vul de inhoud van het gedownloadde publish profile hierin.
1. Voeg de content dit bestand toe bij de inhoud. Geef hem vervolgens de naam `PUBLISH_PROFILE`

## Wijzigingen automatisch publiceren naar Azure omgeving.
Nadat de secret key is gekoppeld met de Git Repository. Worden vanaf nu alle wijzigingen automatisch gepusht via de pipeline naar de Azure Cloud.

## Inrichten Key Vault en Servicebus
:: TODO // Dylan of Brian


