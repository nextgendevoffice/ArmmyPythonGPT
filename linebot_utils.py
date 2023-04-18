from chatgpt_utils import generate_chatgpt_response
from dalle_utils import generate_dalle_image
from linebot.models import ImageSendMessage

def handle_text_message(text):
    if text.lower().startswith("img:"):
        image_prompt = text[13:].strip()
        image_url = generate_dalle_image(image_prompt)[0]
        return ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
    else:
        return TextSendMessage(text=generate_chatgpt_response(text))
