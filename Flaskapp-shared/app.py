import csv
import os
from flask import Flask, render_template, url_for, request, redirect
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
app = Flask(__name__)


# Azure KeyVault name + URL
keyVaultName = "KeyVaultMixit"
KVUri = f"https://{keyVaultName}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

# Get secrets from keyvault "KeyVaultMixit" for acces to servicebus.
retrieved_secret_textdatafromwebapp = client.get_secret("WebAppKeyQuetextdatafromwebapp")
QUEUE_NAME_send = "textdatafromwebapp"

retrieved_secret_quetowebapp = client.get_secret("WebAppKeyQuequetowebapp")
QUEUE_NAME_receive = "quetowebapp"

retrieved_secret_fromwebappwheatherdata = client.get_secret("WebAppKeyQuefromwebappwheatherdata")
QUEUE_NAME_WeatherAPISendQue = "fromwebappwheatherdata"

retrieved_secret_fromweerapptowebapp = client.get_secret("WebAppKeyQuefromweerapptowebapp")
QUEUE_NAME_WeatherAPIReceiveQue = "fromweerapptowebapp"

# For troubleshooting key vault
#print(retrieved_secret_textdatafromwebapp.value)
#print(retrieved_secret_quetowebapp.value)
#print(retrieved_secret_fromwebappwheatherdata.value)
#print(retrieved_secret_fromweerapptowebapp.value)

# Render default page
@app.route('/')
def homepage():
    return render_template('index.html')

# When user use button "Verzenden" on webpage index.html then it enters this function
@app.route('/', methods=['POST'])
def UserInputDataField():
    # User data goes into variable
    UserInputData = request.form.get("UserInputDataFromField")

    # Send user input to function for a servicebus

    # Servicebus Send que: fromwebappwheatherdata
    send_single_message_to_weatherfunction_que(UserInputData)

    # Servicebus Received que: fromwebappwheatherdata
    weerAppReturnData = received_single_message_from_WeerApp()

    # Servicebus Send que: textdatafromwebapp (not in use)
    #send_single_message(UserInputData)

    # Servicebus Received que: textdatafromwebapp (not in use)
    #functionAppReturnData = received_single_message()

    # Return index.html and new variable from servicebus
    return render_template("index.html", UserInputData=UserInputData, weerAppReturnData=weerAppReturnData)
    
# Code for send a single message for the fromweerapptowebapp.
def send_single_message_to_weatherfunction_que(UserText):
    # retrieved_secret_fromwebappwheatherdata.value get the plaintext value from the secret
    with ServiceBusClient.from_connection_string(retrieved_secret_fromwebappwheatherdata.value) as client:
        with client.get_queue_sender(QUEUE_NAME_WeatherAPISendQue) as sender:
            single_message = ServiceBusMessage(UserText)
            sender.send_messages(single_message)

# Code for receiving a single message for the fromweerapptowebapp.
def received_single_message_from_WeerApp():
    with ServiceBusClient.from_connection_string(retrieved_secret_fromweerapptowebapp.value) as client:
        with client.get_queue_receiver(QUEUE_NAME_WeatherAPIReceiveQue) as receiver:
            received_message = receiver.receive_messages(max_wait_time=1)
            for message in received_message:
                bodyMessage = "Receiving: {}".format(message)
                receiver.complete_message(message)
                return(bodyMessage)

# Code for send a single message for the from other function (Brian).
def send_single_message(UserText):
    with ServiceBusClient.from_connection_string(retrieved_secret_textdatafromwebapp.value) as client:
        with client.get_queue_sender(QUEUE_NAME_send) as sender:
            single_message = ServiceBusMessage(UserText)
            sender.send_messages(single_message)

# Code for receiving a single message for the from other function (Brian).
def received_single_message():
    with ServiceBusClient.from_connection_string(retrieved_secret_quetowebapp.value) as client:
        with client.get_queue_receiver(QUEUE_NAME_receive) as receiver:
            received_message = receiver.receive_messages(max_wait_time=1)
            for message in received_message:
                bodyMessage = "Receiving: {}".format(message)
                receiver.complete_message(message)
                return(bodyMessage)