import requests
from rich import console
from ms_graph import GRAPH_API_ENDPOINT, generate_acces_token



console = console.Console()
APP_ID = "1d512be4-f921-4613-9035-15ea23bd0c07"
SCOPES = ['Calenders.ReatWrite']
access_token = generate_acces_token(APP_ID, SCOPES)
# access_token = """ 
# EwBwA8l6BAAUkj1NuJYtTVha+Mogk+HEiPbQo04AAasEkUdx8oPlh2Hqsd5eYqQ7qWx+sheYj43HDWsGPjm+Y2amKeoOwGq2ngfocGzXtS6XrCvUWlO9TExpvP7Zxyv+1NMj4FKLFxils
# g1X+36ewEHVSdxxD/aFKl2BOp6ELLWcYHXy2Mcfwg1r+/V4wAPLQ7bADOU6FGxRHEG/uLgcq/oKoIYzmjw0xWNtgEP/O2OjhzxtLheAn8gheDYSkw0jwt/D3krAlNU02RL+NPRF97L8Ls9TkCUsrbN81i2f
# cN8eKfOT2nRABKUXDqXLuwY4CQFvdG962Q1Lv76dMGKbIN9t20pF5DSYC73doxeEznsFrOVKDp9dJbTTnBZCGQ8DZgAACO6wpf6RHkKAQAJoRvzSgG+2l1CgI9Q8clWZ5elzEYJUJnCb2l9pnSEfhAHhKg5
# Gz7BChQpD8L7utsnVONnuJc84k4auMvZT/gN9q5uh2vMzH9qriRuLqkUvYOROwp0py7kHiVBuRH9G6auvuGcjJzkaKpoMhG32s1HQhSKbbimtK6hSKsMrn4M3rI/gdF2GLhYSm6IomAMlkBv5OqIPi5tAio
# uJ7O1tyoEKfU+XA0FfeFBfJr7UqtZ3+Y/ILCrZncqXbkR28XRMeKKQPsjuWmO3PsAz1nKg++G/E24Cx16728XfKQehpmRa6IEeAvsMcmjXICodgX4/k4CG5tAf5nseOWiLd/vjk7Zi9tgEH0LukdJkbqapX
# n3tqByzTMgRejQYYibOWvJaF+dtCHM03vaXD/wywoB9JsJOt7VkLESilrtD2grbfDFZO4VvqCVcTVP3iW0nRJRQAeNAsFyPP1sBtNrqmEbeMgs4UH368HEtHuMCTKfwI/fVfbC+tcGVtEr+N1Y+Bsk4mIXb
# KfG421+kTEijiezEyfTgawBec5hE3wyxg/CAFLtCq+eKu0AD+6FfACUgISgxc5DhfGmmu/b2Ptqo7cC7hs+V+s3dHdUKwD1QiC5mYhNww8srl8Q0EXAcG6oYKAfhEbIFCuHg9DtF61OHAaUoGrWTE3DkD24
# IcHUG0QzKlOIktBPn1mMd1e3Wrnbg3IZ3C6M6Va74MjAl/kZZAK6Q0nHk0XN8/uehDRRz4m/H5uNGgLYwk/BN94cKK/Hr9uCNOS2GAg==
# """

def event_detail(event_name, **event_details):
    request_body ={
        'subject': event_name
    }
    for key, val in event_details.items():
        request_body[key] = val
    return request_body

headers = {
    'Authorization':'Bearer  '+ access_token
}
# GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0/'

respone_create = requests.post(
    GRAPH_API_ENDPOINT + f'/me/events',
    headers=headers,
    json=event_detail('Osman Test')
)
console.print(respone_create.json())