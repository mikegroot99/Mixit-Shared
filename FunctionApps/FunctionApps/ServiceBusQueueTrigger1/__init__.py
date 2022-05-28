from http.client import responses
import json
import logging
import string
import requests
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
    graph_data = requests.get(request, headers={'Authorization': 'Bearer ' + token},).json()['value']
    #Convert json to a string so that we can send it back to the second queue
    #Set the value of output to the json to send back
    logging.info('Dit is de output van API: %s',
                  str(graph_data))                        
    testjson = json.dumps(graph_data) 
    #stringGraph_Data = str(graph_data)
    outputOutlookApi.set(testjson)
    #wtf