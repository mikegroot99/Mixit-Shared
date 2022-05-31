import json
import logging
import requests
import azure.functions as func

#The main method that runs when app is triggerd
#The inputRequest is the trigger input

def main(inputRequest: func.ServiceBusMessage,
         outputOutlookApi: func.Out[str]):
    logging.info('\n-->AZURE FUNCTION APP')  
    #Take the input and decode it to a normal string value.         
    message =  inputRequest.get_body().decode('utf-8')

    #Split the message based on ; and put the results in variable: token and request.
    token, request = message.split(';')

    #graph_data = requests.get(request, headers={'Authorization': 'Bearer ' + token}).json()['value']<-- Dit split de agenda punten op.
    graph_data = requests.get(request, headers={'Authorization': 'Bearer ' + token}).json()

    #Transform the json we get from the graph api to a string. 
    testjson = json.dumps(graph_data)
    logging.info('Dit is wat er uitkomt: ' + testjson)

    #Set response from graph api into the output.
    outputOutlookApi.set(testjson)

