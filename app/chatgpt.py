import openai
import os
import requests
import base64
import cloudinary
import cloudinary.uploader
from .cache import cached_requests

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

cloudinary.config(
    cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
    api_key=os.environ['CLOUDINARY_API_KEY'],
    api_secret=os.environ['CLOUDINARY_API_SECRET']
)

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
        n=5,
        size="512x512",
    )

    if response and response['data']:
        image_url = response['data'][0]['url']
    return image_url

def upload_image_to_cloudinary(image_url):
    response = cloudinary.uploader.upload(image_url)
    return response['secure_url']
