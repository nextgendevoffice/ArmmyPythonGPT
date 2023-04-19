from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from .chatgpt import generate_response, generate_image, download_image
import os

line_bp = Blueprint('line_bot', __name__)

LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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
    text = event.message.text
    reply = None
    image_data = None

    if text.startswith('/img'):
        prompt = text[4:].strip()
        if prompt:
            image_url = generate_image(prompt)
            if image_url:
                image_data = download_image(image_url)
    else:
        reply = generate_response(text)

    if image_data:
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=f"data:image/jpeg;base64,{image_data}",
                preview_image_url=f"data:image/jpeg;base64,{image_data}",
            ),
        )
    elif reply:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply),
        )
