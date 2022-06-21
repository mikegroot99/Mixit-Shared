import logging

from matplotlib.pyplot import text

import azure.functions as func

from twilio.rest import Client 


def main(inputRequest: func.ServiceBusMessage):
    message =  inputRequest.get_body().decode('utf-8')
    phoneNumber, textMessage = message.split(';')
    token = 'dff6e5233a2d0cf4f13803935618db5e'
    account_sid = 'AC2c599b44820bb7c7d3e6e87d034193d9' 
    client = Client(account_sid, token) 
    
    client.messages.create(
                messaging_service_sid='MGe6ac8db4ff80d266d21e4086f63077ec', 
                body= textMessage,
                to= phoneNumber)  
