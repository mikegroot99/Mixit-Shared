import csv
import os
import requests
import json
import msal
from sqlalchemy import null
import app_config
from flask import Flask, render_template, url_for, request, redirect, session
from flask_session import Session 
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, AzureCliCredential
# Import for proxy fix
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

app.config.from_object(app_config)
debug=True
app.config["TEMPLATES_AUTO_RELOAD"]= True
Session(app)
#test
# Proxy fix for redirect URL.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Azure KeyVault name + URL
keyVaultName = "MixitKeyVault"
KVUri = f"https://{keyVaultName}.vault.azure.net"

# For auto selecting user/identity, if run local, it use users, if in webapp on azure, it runs on managed identity of the webapp.
credential = DefaultAzureCredential()
# credential = AzureCliCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

# Get secrets from keyvault "MixitKeyVaultWebapp" for acces to servicebus.

# The first variable gets que string, the second variable sets que name.
sendsmsque = client.get_secret("sendsmsque")
sendsmsquename = "smsrequestqueue"

sendque = client.get_secret("sendque")
sendquename = "input-queue"

requestque = client.get_secret("requestque")
requestquename = "output-queue"

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

@app.route('/date', methods=['GET', 'POST'])
def date():
    if request.method =="POST":
        print('\n--> is POST request')
        # input_date = request.form.get('date')
        start_date = request.form['start-date']
        end_date = request.form['end-date']


        app_config.TESTDATE = f'https://graph.microsoft.com/v1.0/me/calendarview?startdatetime={start_date}T00:00:00.978Z&enddatetime={end_date}T23:59:18.979Z'
        # app_config.TESTDATE = f'https://graph.microsoft.com/v1.0/me/calendarview?startdatetime=2022-06-13T10:10:18&enddatetime=2022-06-16T10:10:18'                        
        return redirect('/graphcall')
    else:
        print('--> is GET request')
    
    return render_template("date.html")
# When user clicks on "Agenda ophalen" it triggers this /graphcall function
@app.route("/graphcall")
def graphcall():

    print(request.args)
    # This checks if the user have already an exsisting token in the cache, if not then redirecte to the login page.
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    print(f'\nDEFAULT--> {app_config.CENDPOINT}')
    print(f'\nTEST   --> {app_config.TESTDATE}')
    # access token set in new variable
    accestoken = token['access_token']

    print(f'access token: {accestoken}')

    # send token + app_config.Cendpoint to servicebus queue
    send_single_message_to_outlookoutputqueue(accestoken, app_config.TESTDATE)
    # recive all agenda data from queue
    data = received_single_message_from_requestqueue(accestoken)

    # from json to dicts
    # This if statement looked if data returned from service bus que. Otherwise it will crash the app if it is empty.
    if data != "None":
        json_data = json.loads(data)['value']
        # return schedule.html page with agenda data
        return render_template('schedule.html', json_data=json_data)
    else:
        return "Geen data vanuit servicebus"


# This funciton is triggerd when the user logout from the webapp.  
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

# This function is triggerd when user send sms
@app.route("/sendsms", methods=['POST'])
def sendsms():
    nullsixnumber = request.form.get("06nummer")
    smstext = request.form.get("smstext")

    sendsmstoque(nullsixnumber, smstext)

    print(nullsixnumber + ";" + smstext)
    print("In sendsms")
    #return None;
    return redirect(request.referrer)

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
def send_single_message_to_outlookoutputqueue(accestoken, CENDPOINT):
    # retrieved_secret_fromwebappwheatherdata.value get the plaintext value from the secret
    with ServiceBusClient.from_connection_string(sendque.value) as client:
        with client.get_queue_sender(sendquename) as sender:
            #tokenstring = json.dumps(accestoken)
            tokenAndCendpoint = accestoken +";"+ CENDPOINT
            single_message = ServiceBusMessage(tokenAndCendpoint)
            #print("This is the singel message")
            #print(single_message)
            sender.send_messages(single_message)
    print('Ze zijn verstuurd')

#Get single message from Graph output queue
#Checks the token first to make sure its your data
def received_single_message_from_requestqueue(accesstoken):
    print('GET MESSAGE FROM SERVICE BUS')
    verifyDataWithToken(requestque, requestquename, accesstoken)
    with ServiceBusClient.from_connection_string(requestque.value) as client:
        with client.get_queue_receiver(requestquename) as receiver:
            # If token is a match recieve the message and complete it.            
            received_message = receiver.receive_messages() 
            for message in received_message:
                #Message needs to be a string to preform the split function
                messageToString = str(message)       
                token, data = messageToString.split('==ç') 
                receiver.complete_message(message)
                return(data)
                
#outputQueue = the connection string for the queue from the keyvault
#queueName = The name of the output queue
#accessToken = The token that is send to the service bus when a request is made
def verifyDataWithToken(outputQueue, queueName, accessToken):
    with ServiceBusClient.from_connection_string(outputQueue.value) as client:
        with client.get_queue_receiver(queueName) as receiver:
            token = "null"
            # While loop peeks at the first message and compares the tokens.
            while token != accessToken:
                    print("Token is not a match")
                    peek_message = receiver.peek_messages(max_message_count=1)
                    for peekMessage in peek_message:
                        peekMessage = str(peekMessage)
                        print(peekMessage)
                        token, data = peekMessage.split('==ç')
                        if token == accessToken:
                            continue

# For sending sms
def sendsmstoque(nullsixnumber, smstext):
    # retrieved_secret_fromwebappwheatherdata.value get the plaintext value from the secret
    with ServiceBusClient.from_connection_string(sendsmsque.value) as client:
        with client.get_queue_sender(sendsmsquename) as sender:
            #tokenstring = json.dumps(accestoken)
            numberPlusSMStext = nullsixnumber +";"+ smstext
            single_message = ServiceBusMessage(numberPlusSMStext)
            #print("This is the singel message")
            #print(single_message)
            sender.send_messages(single_message)
    print('Ze zijn verstuurd')


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