from http.client import responses
import logging
import requests
import json
import azure.functions as func

#The main method that runs when app is triggerd
#The inputRequest is the trigger input
#The outputWeatherAPI is the output these are defined in the function.json
def main(inputRequest: func.ServiceBusMessage,
         outputWeatherAPI: func.Out[str]):
    # Log the input so we can see what it gets from the queue
    logging.info('Python ServiceBus queue trigger processed message: %s',
                 inputRequest.get_body().decode('utf-8'))
    #Create the request URL for the weather API with the input from the queue
    message =  inputRequest.get_body().decode('utf-8')
    api_url = "https://api.openweathermap.org/data/2.5/weather?q=" + message + "&appid=a6c60d1395554bbac92f34b7ebf8122d"
    #Request data from weather API with URL
    response = requests.get(api_url)
    #Log the response of the Weather API so we can see what it sends back
    logging.info(response.json())
    #Convert json to a string so that we can send it back to the second queue
    data = json.loads(response.text)
    jsonToString = json.dumps(data)
    #Set the value of output to the json to send back
    outputWeatherAPI.set(jsonToString)
    #wtf