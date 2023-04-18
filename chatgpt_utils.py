import requests
import os

def generate_chatgpt_response(prompt):
    api_key = os.environ['OPENAI_API_KEY']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': 'gpt-3.5-turbo',  # Adjust the model to your desired GPT model
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.8,
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)
    response_data = response.json()
    generated_text = response_data['choices'][0]['message']['content'].strip()

    return generated_text
