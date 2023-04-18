import os
import logging
import asyncio
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from linebot_utils import handle_text_message

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

async def reply_message(reply_token, text):
    await asyncio.sleep(2) # add a sleep to simulate a delay
    message = TextSendMessage(text=text)
    line_bot_api.reply_message(reply_token, message)

@app.route('/webhook', methods=['POST'])
def webhook():
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
def handle_message(event):
    reply_token = event.reply_token
    prompt = event.message.text

    # Generate response asynchronously
    response = asyncio.run(handle_text_message(prompt))

    # Reply to the user's message
    asyncio.create_task(reply_message(reply_token, response))

if __name__ == "__main__":
    app.run()
