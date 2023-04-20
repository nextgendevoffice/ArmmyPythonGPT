import os
import logging
import openai
from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from .chatgpt import generate_response
from .database import get_user_tokens, update_user_tokens
from .database import save_chat_history, get_chat_history
import thai_translation_model
import image_generation_model


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

line_bp = Blueprint('line_bot', __name__)

LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

openai.api_key = os.environ['OPENAI_API_KEY']

def generate_image_from_thai_text(thai_text):
    # Preprocess Thai text input for translation model
    input_data = thai_translation_model.preprocess(thai_text)

    # Translate Thai text to English
    english_text = thai_translation_model.translate(input_data)

    # Preprocess English text input for image generation model
    input_data = image_generation_model.preprocess(english_text)

    # Generate image using the English text
    image = image_generation_model.generate_image(openai.api_key, input_data)

    # Post-process and return the generated image
    return image


def generate_dalle_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="url"
    )

    image_url = response['data'][0]['url']
    return image_url

@line_bp.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    logging.info("Handling event: %s", event)

    user_id = event.source.user_id
    text = event.message.text
    tokens = get_user_tokens(user_id)

    if tokens is None:
        tokens = 3000
        update_user_tokens(user_id, tokens)

    if text.startswith('/img'):
        prompt = text[4:].strip()
        image_url = generate_image_from_thai_text(prompt)  # Change this line
        image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
        line_bot_api.reply_message(event.reply_token, image_message)
    elif text.startswith('/tokens'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"ปัจจุบันคุณมี {tokens} tokens."))
    elif text.startswith('/user'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"User ID ของคุณคือ: {user_id}"))
    elif text.startswith('/history'):
        chat_history = get_chat_history(user_id)
        history_text = "\n\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in chat_history])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=history_text))
    else:
        response = generate_response(text)
        save_chat_history(user_id, text, response)  # Save the chat history
        logging.info("Generated response: %s", response)
        tokens_used = len(response)
        new_tokens = tokens - tokens_used

        if new_tokens < 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="คุณใช้ Token 3,000 Token ฟรี หมดแล้ว. หากคุณต้องการใช้งานกรุณาเติมเงินเพื่อใช้งานอย่างต่อเนื่อง!!"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
            update_user_tokens(user_id, new_tokens)