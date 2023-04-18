import aiohttp
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

async def generate_chatgpt_response(prompt):
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

    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers) as response:
            response_data = await response.json()
            generated_text = response_data['choices'][0]['message']['content'].strip()

            # Log the prompt and generated response
            logger.info(f"User prompt: {prompt}")
            logger.info(f"Generated response: {generated_text}")

            return generated_text

async def get_response_with_timeout(prompt, timeout=300):
    try:
        response = await asyncio.wait_for(generate_chatgpt_response(prompt), timeout=timeout)
    except asyncio.TimeoutError:
        response = "Sorry, I'm taking too long to respond. Please try again later."
    return response
