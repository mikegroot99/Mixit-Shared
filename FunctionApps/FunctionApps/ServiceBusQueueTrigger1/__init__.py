from ast import AsyncFunctionDef
from http.client import responses
import json
import logging
import string
import requests
import azure.functions as func
from azure.servicebus import ServiceBusClient, ServiceBusMessage

#The main method that runs when app is triggerd
#The inputRequest is the trigger input
#The outputWeatherAPI is the output these are defined in the function.json

def main(inputRequest: func.ServiceBusMessage,
         outputOutlookApi: func.Out[str]):
    logging.info('\n-->AZURE FUNCTION APP')           
    message =  inputRequest.get_body().decode('utf-8')
    
    token, request = message.split(';')
    #graph_data = requests.get(request, headers={'Authorization': 'Bearer ' + token}).json()['value']<-- Dit split de agenda punten op 
    graph_data = requests.get(request, headers={'Authorization': 'Bearer ' + token}).json()

    testjson = json.dumps(graph_data)
    logging.info('Dit is wat er uitkomt: ' + testjson)
    outputOutlookApi.set(testjson)