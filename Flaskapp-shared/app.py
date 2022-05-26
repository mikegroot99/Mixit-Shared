import csv
import os
import requests
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


# Old keyvault code.

# Azure KeyVault name + URL
keyVaultName = "KeyVaultMixit"
KVUri = f"https://{keyVaultName}.vault.azure.net"

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
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    print(token)
    #Ophalen data met graph API
    graph_data = requests.get(
        app_config.CENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()['value']
    print(graph_data)
    return render_template('schedule.html', data=graph_data)

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

# Send data to servicebus bellow

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