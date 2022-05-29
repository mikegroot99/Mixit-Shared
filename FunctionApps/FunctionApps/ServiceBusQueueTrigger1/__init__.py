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
    graph_data = requests.get(request, headers={'Authorization': 'Bearer ' + token}).json()

    testjson = json.dumps(graph_data) 
    logging.info('Dit is wat er uitkomt: ' + testjson)
    send_single_message(testjson)
#     outputOutlookApi.set(testjson)

CONNECTION_STR = 'Endpoint=sb://mixitservicebus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=1Q9s7l1qBxe+2ClvoAVLtAVBHGviqWN9ut6Jr9IgVto='
QUEUE_NAME = 'output-queue-2'
servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
# Send to service bus 
def send_single_message(input):

    logging.info('\n--------------\n')
    logging.info(input)
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)

    message = ServiceBusMessage(input)    
    sender.send_messages(message)
    print("\n --> DONE SENDIN")
