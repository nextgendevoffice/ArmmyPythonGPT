import os
import logging
import openai
from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from .chatgpt import generate_response
from .database import get_user_tokens, update_user_tokens

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

line_bp = Blueprint('line_bot', __name__)

LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

openai.api_key = os.environ['OPENAI_API_KEY']

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
        image_url = generate_dalle_image(prompt)
        image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
        line_bot_api.reply_message(event.reply_token, image_message)
    elif text.startswith('/tokens'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"You have {tokens} tokens remaining."))
    else:
        response = generate_response(text)
        logging.info("Generated response: %s", response)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

        tokens_used = len(response)
        new_tokens = tokens - tokens_used

        if new_tokens < 0:
            line_bot_api.push_message(user_id, TextSendMessage(text="You've used all your free tokens Kub. Please purchase more tokens to continue using the service."))
        else:
            update_user_tokens(user_id, new_tokens)
