import os
import requests

def generate_dalle_image(prompt, model="image-alpha-001", num_images=1):
    api_key = os.environ['OPENAI_API_KEY']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': model,
        'prompt': prompt,
        'num_images': num_images
    }

    response = requests.post('https://api.openai.com/v1/images/generations', json=data, headers=headers)
    response_data = response.json()

    images = response_data['data']
    image_urls = [image['url'] for image in images]

    return image_urls
