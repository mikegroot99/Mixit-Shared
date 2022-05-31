import logging

import azure.functions as func


def main(inputGraphApi: func.ServiceBusMessage, outputGraphApi: func.Out[str]):
    logging.info('Python ServiceBus queue trigger processed message: %s',
                 inputGraphApi.get_body().decode('utf-8'))
    outputGraphApi.set(inputGraphApi + 'Dit is een aanpassing')
