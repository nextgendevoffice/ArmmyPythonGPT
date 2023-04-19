import openai
import os
import requests
import base64
from .cache import cached_requests

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

@cached_requests
def generate_response(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message['content'].strip()

def generate_image(prompt):
    image_url = None

    response = openai.Image.create(
        model="image-alpha-001",
        prompt=prompt,
        n=1,
        size="256x256",
    )

    if response and response['data']:
        image_url = response['data'][0]['url']
    return image_url

def download_image(image_url):
    response = requests.get(image_url)
    return base64.b64encode(response.content).decode('utf-8')
