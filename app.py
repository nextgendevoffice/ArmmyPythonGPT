import os
import logging
import asyncio
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from chatgpt_utils import generate_chatgpt_response

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

async def reply_message(reply_token, response):
    try:
        await line_bot_api.reply_message(reply_token, TextSendMessage(text=response))
    except Exception as e:
        logger.error(e)

@app.route('/webhook', methods=['POST'])
async def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    logger.info(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature. Check your LINE_CHANNEL_SECRET.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
async def handle_message(event):
    reply_message_task = asyncio.create_task(reply_message(event.reply_token, generate_chatgpt_response(event.message.text)))
    await reply_message_task

if __name__ == "__main__":
    asyncio.run(app.run(debug=True))
