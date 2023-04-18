import requests
import os

def generate_chatgpt_response(prompt):
    api_key = os.environ['OPENAI_API_KEY']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': 'text-davinci-003',  # Updated to use text-davinci-003
    }

    response = requests.post('https://api.openai.com/v1/completions', json=data, headers=headers)
    response_data = response.json()
    generated_text = response_data['choices'][0]['text'].strip()

    return generated_text
