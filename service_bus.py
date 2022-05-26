# import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage
import time


CONNECTION_STR = "Endpoint=sb://mixit-team-2.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=GiA2uZW4OzIzPZmH/7caW1+YyOjMOHDDAuIsCtN9/ic="
QUEUE_NAME = "input-queue"

def connect_to_service_bus():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
    return servicebus_client

def send_single_message(sender,userInput):
    message = ServiceBusMessage(userInput)
    sender.send_messages(message)
    print("Sent a single message")

# def send_a_list_of_messages(sender):
#     messages = [ServiceBusMessage("Message in list") for _ in range(5)]
#     sender.send_messages(messages)
#     print("Sent a list of 5 messages")

# def send_batch_message(sender):
#     batch_message = sender.create_message_batch()
#     for _ in range(10):
#         try:
#             batch_message.add_message(ServiceBusMessage("Message inside a ServiceBusMessageBatch"))
#         except ValueError:
#             # ServiceBusMessageBatch object reaches max_size.
#             # New ServiceBusMessageBatch object can be created here to send more data.
#             break
#     sender.send_messages(batch_message)
#     print("Sent a batch of 10 messages")


#CLient aamaken NODIG
def send_to_servicebus(userInput):
    print('--> SEND Service Bus data')
    servicebus_client = connect_to_service_bus()

    with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        with sender:
            send_single_message(sender, userInput)
            # send_a_list_of_messages(sender)
            # send_batch_message(sender)

def get_from_servicebus():
    time.sleep(1)
    print('--> Get Service Bus data')

    servicebus_client = connect_to_service_bus()
    QUEUE_NAME = "output-queue"
    message_list = []
    print('--> GET Service Bus data')        
    with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=5)
        with receiver:
            for msg in receiver:
                print("Received: " + str(msg))
                receiver.complete_message(msg)
                message_list.append(str(msg))
    
    return message_list             


send_to_servicebus('')


get_from_servicebus()