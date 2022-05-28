import csv
import os
import requests
import json
from flask import Flask, render_template, url_for, request, redirect, session
from flask_session import Session 
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import msal
import app_config

app = Flask(__name__)

app.config.from_object(app_config)
Session(app)


# serviceque connection strings
# function app (brian) azure location
sendque = "Endpoint=sb://mixitservicebus.servicebus.windows.net/;SharedAccessKeyName=conncetionRequestQueue;SharedAccessKey=73BwiAWHM7diJ/kRmw2RUGiGL0zkAlBSnjndTWwB3gY=;EntityPath=outlookrequestqueue"
sendquename = "outlookrequestqueue"

requestque =  "Endpoint=sb://mixitservicebus.servicebus.windows.net/;SharedAccessKeyName=conncetionOutputQueue;SharedAccessKey=ozFfiZwPe84DJt3v7T2u/sUM2egubyolpV2eTxr6zWM=;EntityPath=outlookoutputqueue"
requestquename = "outlookoutputqueue"

# function app (wessel) local pc locations

sendqueWessel= "Endpoint=sb://mixitservicebus.servicebus.windows.net/;SharedAccessKeyName=input-connection-string;SharedAccessKey=SYSco7xYz+hmt7AF7qZx6dm8ZybeZPOZ7LAHmohUnl8=;EntityPath=input-queque-2"
sendquenameWessel= "input-queque-2"

requestqueWessel = "Endpoint=sb://mixitservicebus.servicebus.windows.net/;SharedAccessKeyName=output-queue-2;SharedAccessKey=t5xF10WVDwWzBBZpgXtYpKyhpz4hUeSbnbZ9k/+yVfU=;EntityPath=output-queue-2"
requestquenameWessel = "output-queue-2"
# Old keyvault code.

# Azure KeyVault name + URL
#keyVaultName = "KeyVaultMixit"
#KVUri = f"https://{keyVaultName}.vault.azure.net"

#credential = DefaultAzureCredential()
#client = SecretClient(vault_url=KVUri, credential=credential)

# Get secrets from keyvault "KeyVaultMixit" for acces to servicebus.
#retrieved_secret_textdatafromwebapp = client.get_secret("WebAppKeyQuetextdatafromwebapp")
#QUEUE_NAME_send = "textdatafromwebapp"

#retrieved_secret_quetowebapp = client.get_secret("WebAppKeyQuequetowebapp")
#QUEUE_NAME_receive = "quetowebapp"

#retrieved_secret_fromwebappwheatherdata = client.get_secret("WebAppKeyQuefromwebappwheatherdata")
#QUEUE_NAME_WeatherAPISendQue = "fromwebappwheatherdata"

#retrieved_secret_fromweerapptowebapp = client.get_secret("WebAppKeyQuefromweerapptowebapp")
#QUEUE_NAME_WeatherAPIReceiveQue = "fromweerapptowebapp"

# For troubleshooting key vault
#print(retrieved_secret_textdatafromwebapp.value)
#print(retrieved_secret_quetowebapp.value)
#print(retrieved_secret_fromwebappwheatherdata.value)
#print(retrieved_secret_fromweerapptowebapp.value)

# Website redirects

# When user use button "Verzenden" on webpage index.html then it enters this function
@app.route('/')
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template('index.html', user=session["user"], version=msal.__version__)
    
    
    # Old code to servicebus and other things 

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

@app.route("/login")
def login():
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

@app.route("/graphcall")
def graphcall():
    print('\n-------GET --------')
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    #print(token)

    # Acces token
    accestoken = token['access_token']
    # send token + app_config.Cendpoint to servicebus que
    send_single_message_to_outlookoutputqueuee(accestoken, app_config.CENDPOINT)
    # send_single_message_to_outlookoutputqueueeWessel(accestoken, app_config.CENDPOINT)
    retrievedDataFromRequestquee = received_single_message_from_requestque()

    #print(graph_data)
    print('------')
    print('HIERZOOOO')
    print(type(retrievedDataFromRequestquee))
    
    data = str(retrievedDataFromRequestquee)
    
    json_data = json.loads(data)
    
    print('--> JA HALLO DIT IS JSON DATA')
    tijd = json_data['start']['dateTime'][0]

    #print(retrievedDataFromRequestquee)
    # jsonRetrievedDataFromRequestquee = json.loads(retrievedDataFromRequestquee)
    
    print(json_data['start'])
    
    # print(jsonRetrievedDataFromRequestquee)
    return render_template('schedule.html', json_data=json_data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

@app.route(app_config.REDIRECT_PATH)  # Applicatie URI 
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:
        pass
    return redirect(url_for("index"))

# Send and retrieve data to servicebus (nieuw)

# Code for send a single message to outlookoutputqueue (brian) for getting agenda
def send_single_message_to_outlookoutputqueuee(accestoken, CENDPOINT):
    # retrieved_secret_fromwebappwheatherdata.value get the plaintext value from the secret
    with ServiceBusClient.from_connection_string(sendque) as client:
        with client.get_queue_sender(sendquename) as sender:
            #tokenstring = json.dumps(accestoken)
            tokenAndCendpoint = accestoken +";"+ CENDPOINT
            single_message = ServiceBusMessage(tokenAndCendpoint)
            #print("This is the singel message")
            #print(single_message)
            sender.send_messages(single_message)
    print('Ze zijn verstuurd')

# Code for retrieve a single message to outlookoutputqueue (brian) for getting agenda
def received_single_message_from_requestque():
    print('GET MESSAGE FROM SERVICE BUS')
    with ServiceBusClient.from_connection_string(requestque) as client:
        with client.get_queue_receiver(requestquename) as receiver:
            received_message = receiver.receive_messages(max_wait_time=1)
            for message in received_message:
                receiver.complete_message(message)
                return(message)



# Code for send a single message to outlookoutputqueue (Wessel) for getting agenda
def send_single_message_to_outlookoutputqueueeWessel(accestoken, CENDPOINT):
    # retrieved_secret_fromwebappwheatherdata.value get the plaintext value from the secret
    with ServiceBusClient.from_connection_string(sendqueWessel) as client:
        with client.get_queue_sender(sendquenameWessel) as sender:
            #tokenstring = json.dumps(accestoken)
            tokenAndCendpoint = accestoken +";"+ CENDPOINT
            single_message = ServiceBusMessage(tokenAndCendpoint)
            #print("This is the singel message")
            #print(single_message)
            sender.send_messages(single_message)



# Send data to servicebus bellow old

# Code for receiving a single message for the fromweerapptowebapp.
def received_single_message_from_WeerApp():
    with ServiceBusClient.from_connection_string(retrieved_secret_fromweerapptowebapp.value) as client:
        with client.get_queue_receiver(QUEUE_NAME_WeatherAPIReceiveQue) as receiver:
            received_message = receiver.receive_messages(max_wait_time=1)
            for message in received_message:
                bodyMessage = "Receiving: {}".format(message)
                receiver.complete_message(message)
                return(bodyMessage)


# Team 2 code bellow


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template