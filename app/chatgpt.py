import openai
import os
from .cache import cached_requests
from tiktoken import Tokenizer

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY
tokenizer = Tokenizer()

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

    answer = response.choices[0].message['content'].strip()
    
    # Calculate token counts using tiktoken
    prompt_tokens = len(list(tokenizer.tokenize(prompt)))
    completion_tokens = len(list(tokenizer.tokenize(answer)))
    total_tokens = prompt_tokens + completion_tokens

    return answer, prompt_tokens, completion_tokens, total_tokens
