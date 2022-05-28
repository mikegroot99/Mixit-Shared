from http.client import responses
import logging
import string
import requests
import json
import azure.functions as func

#The main method that runs when app is triggerd
#The inputRequest is the trigger input
#The outputWeatherAPI is the output these are defined in the function.json
def main(inputRequest: func.ServiceBusMessage,
         outputOutlookApi: func.Out[str]):
    # Log the input so we can see what it gets from the queue
    logging.info('Python ServiceBus queue trigger processed message: %s',
                 inputRequest.get_body().decode('utf-8'))
    #Create the request URL for the weather API with the input from the queue
    message =  inputRequest.get_body().decode('utf-8')
    token, request = message.split(';')
    graph_data = requests.get(request, headers={'Authorization': 'Bearer ' + token},).json()
    #Convert json to a string so that we can send it back to the second queue
    #Set the value of output to the json to send back
    outputOutlookApi.set(str(graph_data))
    #wtf