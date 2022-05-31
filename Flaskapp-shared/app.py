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

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Services bus que's to the function app for microsoft GRAPH API.
sendque = "Endpoint=sb://mixitservicebus.servicebus.windows.net/;SharedAccessKeyName=conncetionRequestQueue;SharedAccessKey=73BwiAWHM7diJ/kRmw2RUGiGL0zkAlBSnjndTWwB3gY=;EntityPath=outlookrequestqueue"
sendquename = "outlookrequestqueue"

requestque =  "Endpoint=sb://mixitservicebus.servicebus.windows.net/;SharedAccessKeyName=conncetionOutputQueue;SharedAccessKey=ozFfiZwPe84DJt3v7T2u/sUM2egubyolpV2eTxr6zWM=;EntityPath=outlookoutputqueue"
requestquename = "outlookoutputqueue"

# azure key vault not in use at the moment!

# Azure KeyVault name + URL
#keyVaultName = "Mixit-shared-key-vault"
#KVUri = f"https://{keyVaultName}.vault.azure.net"

#credential = DefaultAzureCredential()
#client = SecretClient(vault_url=KVUri, credential=credential)

# Get secrets from keyvault "KeyVaultMixit" for acces to servicebus. (Not in use at the moment)
#retrieved_secret_textdatafromwebapp = client.get_secret("outlookoutputqueue")
#QUEUE_NAME_send = "outlookoutputqueue"

#retrieved_secret_textdatafromwebapp = client.get_secret("outlookrequestqueue")
#QUEUE_NAME_receive = "outlookrequestqueue"

#retrieved_secret_textdatafromwebapp = client.get_secret("Client-secret-web-app")
#CLIENT_WEB_secret = "Client-secret-web-app"

#retrieved_secret_textdatafromwebapp = client.get_secret("Client-id-web-app")
#CLIENT_ID_secret= "Client-id-web-app"

# Website redirects
@app.route('/')
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template('index.html', user=session["user"], version=msal.__version__)

@app.route("/login")
def login():
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

# When user clicks on "Agenda ophalen" it triggers this /graphcall function
@app.route("/graphcall")
def graphcall():
    # This checks if the user have already an exsisting token in the cache, if not then redirecte to the login page.
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))

    # access token set in new variable
    accestoken = token['access_token']

    # send token + app_config.Cendpoint to servicebus que
    send_single_message_to_outlookoutputqueuee(accestoken, app_config.CENDPOINT)
    # recive all agenda data from que
    retrievedDataFromRequestquee = received_single_message_from_requestque()

    # data from servicebus to string and in new variable
    data = str(retrievedDataFromRequestquee)
    # from json to dicts
    json_data = json.loads(data)['value']
    # return schedule.html page with agenda data
    return render_template('schedule.html', json_data=json_data)

# This funciton is triggerd when the user logout from the webapp.  
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

# function for checking auth validation
@app.route(app_config.REDIRECT_PATH)
def authorized():
    try:
        cache = _load_cache()
        # Validate the auth response being redirected back, and obtain tokens.
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:
        pass
    return redirect(url_for("index"))

# Functions for send and retrieve data from servicebus

# Code for send a single message to outlookoutputqueue for getting agenda
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

# Code for retrieve a single message to outlookoutputqueue for getting agenda
def received_single_message_from_requestque():
    print('GET MESSAGE FROM SERVICE BUS')
    with ServiceBusClient.from_connection_string(requestque) as client:
        with client.get_queue_receiver(requestquename) as receiver:
            received_message = receiver.receive_messages(max_wait_time=1)
            for message in received_message:   
                receiver.complete_message(message)
                return(message)

# functions for functions above

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