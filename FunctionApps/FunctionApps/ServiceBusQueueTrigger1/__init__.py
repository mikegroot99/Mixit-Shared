import json
import logging
import requests
import azure.functions as func

#The main method that runs when app is triggerd
#The inputRequest is the trigger input

def main(inputRequest: func.ServiceBusMessage,
         outputOutlookApi: func.Out[str]):
    #Take the input and decode it to a normal string value.         
    message =  inputRequest.get_body().decode('utf-8')
    #Split the message based on ; and put the results in variable: token and request.
    token, request = message.split(';')
    #Use to token and request variable to communicate with the graph api.
    graph_data = requests.get(request, headers={'Authorization': 'Bearer ' + token}).json()
    #Transform the json we get from the graph api to a string. 
    graphResponse = json.dumps(graph_data)
    #Set response from graph api into the output.
    #We send the token back for data authentication
    outputOutlookApi.set(token + "==ç" + graphResponse)