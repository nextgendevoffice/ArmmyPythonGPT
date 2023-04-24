import openai
import os
from .cache import cached_requests
import time

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

@cached_requests
def generate_response(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    start_time = time.time()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )
    end_time = time.time()
    gpt_response_time = end_time - start_time
    answer = response.choices[0].message['content'].strip()
    prompt_tokens = response['usage']['prompt_tokens']
    completion_tokens = response['usage']['completion_tokens']
    total_tokens = response['usage']['total_tokens']

    return answer, prompt_tokens, completion_tokens, total_tokens
