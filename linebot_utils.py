from chatgpt_utils import generate_chatgpt_response

def handle_text_message(text):
    response_text = generate_chatgpt_response(text)
    return response_text
