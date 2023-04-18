import requests
import os
import logging

logger = logging.getLogger(__name__)

def generate_chatgpt_response(prompt):
    api_key = os.environ['OPENAI_API_KEY']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': 'gpt-3.5-turbo',  # Adjust the model to your desired GPT model
        'messages': [
            {'role': 'system', 'content': 'สวัสดีจ๋ะนายจ๋า ฉันชื่อ อับดุลเอ๋ย. นายมีอะไรให้อับดุลช่วยไหมจ๋ะนายจ๋า'},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.8,
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)
    response_data = response.json()
    generated_text = response_data['choices'][0]['message']['content'].strip()

    # Log the prompt and generated response
    logger.info(f"User prompt: {prompt}")
    logger.info(f"Generated response: {generated_text}")

    return generated_text
