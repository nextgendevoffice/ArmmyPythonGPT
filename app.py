import os
import logging
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from chatgpt_utils import get_response_with_timeout
from linebot_utils import handle_text_message

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

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
    reply_message = handle_text_message(event.message.text)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
    
async def handle_text_message(text):
    response_text = await get_response_with_timeout(text)
    return response_text
if __name__ == "__main__":
    app.run()
