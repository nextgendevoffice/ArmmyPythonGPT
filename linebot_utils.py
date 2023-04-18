import os
from chatgpt_utils import generate_chatgpt_response
from dalle_utils import generate_dalle_image
from linebot.models import TextSendMessage, ImageSendMessage
from google.cloud import translate_v2 as translate

translate_client = translate.Client.from_api_key(os.environ['GOOGLE_CLOUD_API_KEY'])

def translate_text(text, target_language='en'):
    result = translate_client.translate(text, target_language=target_language)
    return result['translatedText']

def handle_text_message(text):
    if text.lower().startswith("img:"):
        image_prompt = text[4:].strip()
        image_prompt_english = translate_text(image_prompt)
        image_url = generate_dalle_image(image_prompt_english)[0]
        return ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
    else:
        return TextSendMessage(text=generate_chatgpt_response(text))
