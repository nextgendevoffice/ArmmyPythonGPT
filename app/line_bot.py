import os
import logging
import openai
from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from .chatgpt import generate_response
from . import thai_translation_model
from . import image_generation_model
import random
import string
from .database import (get_user_tokens, update_user_tokens, save_chat_history, get_chat_history, create_coupon, add_token, get_token_history, add_admin, is_admin, get_total_users, get_total_tokens_used)
from .database import db
from threading import Thread
import time
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=50)
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


HARDCODED_ADMIN_USER_ID = 'U983968ed313854758775d4b8c05b6f8a'

# Add the hardcoded admin user ID to the database
add_admin(HARDCODED_ADMIN_USER_ID)
# line_bot.py
def check_admin(user_id):
    return is_admin(user_id) # Check admin status in the database


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


# Generate a random coupon code
def generate_coupon_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def create_coupon(tokens):
    coupon_code = generate_coupon_code()
    coupon = {"coupon_code": coupon_code, "tokens": tokens}
    db.coupons.insert_one(coupon)  # Use the db object from your database.py file
    return coupon_code


def add_token(user_id, coupon_code):
    coupon = db.coupons.find_one({"coupon_code": coupon_code})

    if not coupon:
        return "ไม่พบคูปองใบนี้."

    if "user_id" in coupon:
        return "คูปองใบนี้ถุกใช้งานแล้ว."

    # Update user's tokens here
    user = db.users.find_one({"user_id": user_id})
    if user:
        new_tokens = user["tokens"] + coupon["tokens"]
        db.users.update_one({"user_id": user_id}, {"$set": {"tokens": new_tokens}})
    else:
        new_tokens = 3000 + coupon["tokens"]
        db.users.insert_one({"user_id": user_id, "tokens": new_tokens})

    # Log the coupon usage
    db.coupons.update_one({"coupon_code": coupon_code}, {"$set": {"user_id": user_id}})

    return f"คุณเติม Token จำนวน {coupon['tokens']} tokens. เรียบร้อยแล้ว"

def send_waiting_message(user_id):
    waiting_message = "รออับดุลคิดแป๊บนะจ๊ะ!!"
    line_bot_api.push_message(user_id, TextSendMessage(text=waiting_message))

def handle_message_async(event):
    logging.info("Handling event: %s", event)
    user_id = event.source.user_id
    text = event.message.text
    tokens = get_user_tokens(user_id)
    if tokens is None:
        tokens = 3000
        update_user_tokens(user_id, tokens)

        # If the input text has more than 15 characters, start the waiting message thread
    if len(text) > 15:
        waiting_message_thread = Thread(target=send_waiting_message, args=(user_id,))
        waiting_message_thread.start()

    if text.startswith('/img'):
        prompt = text[4:].strip()
        image_url = generate_image_from_thai_text(prompt)
        image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)

        # Define a fixed amount of tokens to be deducted for each generated image
        tokens_used = 1000
        new_tokens = tokens - tokens_used
        # Check if the user has enough tokens to generate an image
        if new_tokens < 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="คุณไม่มีเครดิตพอที่จะสร้างภาพ กรุณาเติมเครดิตก่อน"))
        else:
            line_bot_api.reply_message(event.reply_token, image_message)
            update_user_tokens(user_id, new_tokens)
    elif text.startswith('/tokens'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"ปัจจุบันคุณมี {tokens} tokens."))
    elif text.startswith('/user'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"User ID ของคุณคือ: {user_id}"))
    elif text.startswith('/buytoken'):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"เติมเงินได้ที่ :https://payment.abul-ai.com/?User_id={user_id}"))
    elif text.strip() == '/history':
        chat_history = get_chat_history(user_id)
        history_text = "\n\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in chat_history])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=history_text))
    elif text.startswith('/createcoupon') and check_admin(user_id):
        _, num_coupons, tokens = text.split()
        num_coupons = int(num_coupons)
        tokens = int(tokens)

        created_coupons = []
        for _ in range(num_coupons):
            coupon_code = create_coupon(tokens)
            created_coupons.append(coupon_code)

        reply_text = f"สร้าง {num_coupons} คูปอง จำนวน {tokens} tokens เรียบร้อยแล้ว:\n" + "\n".join(created_coupons)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    elif text.startswith('/addcoupon'):
        _, coupon_code = text.split()
        response = add_token(user_id, coupon_code)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
    elif text.strip() == '/historycoupon':
        token_history = get_token_history(user_id)
        if token_history:
            history_text = "\n\n".join([f"Coupon Code: {item['coupon_code']}\nTokens Added: {item['tokens']}" for item in token_history])
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=history_text))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No token history found."))
    elif text.startswith('/addadmin'):
        if check_admin(user_id):
            new_admin_id = text.split()[1]
            add_admin(new_admin_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"Admin {new_admin_id} added successfully."))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="You do not have permission to use this command."))
    elif text.strip() == '/totaluser' and check_admin(user_id):
            total_users = get_total_users()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"Total number of users: {total_users}"))
    elif text.startswith('/usetoken') and check_admin(user_id):
            _, start_date, end_date = text.split()
            total_tokens_used = get_total_tokens_used(start_date, end_date)
            reply_text = f"Total tokens used between {start_date} and {end_date}: {total_tokens_used}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    else:
        start_time = time.time()
        response, prompt_tokens, completion_tokens, total_tokens = generate_response(text)
        end_time = time.time()
        handle_message_time = end_time - start_time
        save_chat_history(user_id, text, response, prompt_tokens, completion_tokens, total_tokens)
        logging.info("Generated response: %s", response)
        tokens_used = total_tokens
        new_tokens = tokens - tokens_used

        if new_tokens < 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="คุณใช้ Token 3,000 Token ฟรี หมดแล้ว. หากคุณต้องการใช้งานกรุณาเติมเงินเพื่อใช้งานอย่างต่อเนื่อง!! แชร์โพสเพื่อรับ Token ฟรี : https://bit.ly/3AeNG6y"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
            update_user_tokens(user_id, new_tokens)
            
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    logging.info("Handling event: %s", event)
    executor.submit(handle_message_async, event)
