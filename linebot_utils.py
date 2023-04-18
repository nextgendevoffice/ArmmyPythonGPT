from chatgpt_utils import generate_chatgpt_response
from dalle_utils import generate_dalle_image
from linebot.models import TextSendMessage, ImageSendMessage
from googletrans import Translator

def translate_text(text, target_language='en'):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language).text
    return translated_text

def handle_text_message(text):
    if text.lower().startswith("img:"):
        image_prompt = text[13:].strip()
        image_prompt_english = translate_text(image_prompt)
        image_url = generate_dalle_image(image_prompt_english)[0]
        return ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
    else:
        return TextSendMessage(text=generate_chatgpt_response(text))