from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import sqlite3
import re

app = Flask(__name__)

# ===== LINE 設定 =====
LINE_CHANNEL_ACCESS_TOKEN = "20xeCWb7gYTJBPgd+VkrAVI5Ca3KFNFNdMZdaCY8Zx9PmQ7aRTn/4qGcnChLPZ79tWASqWD6HG8xIQQMcywBSXfy4ecnc0Do9Jq1w/SwDqzh0qlSC3mik7hlzeZc2XiDi5peDqfoSkTzieRVLdy7QAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "894b0fb1af135212cf6fce2a47be641e"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ===== SQLite =====
DB_NAME = "members.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        line_user_id TEXT PRIMARY KEY,
        birth_month INTEGER
    )
    """)
    conn.commit()
    conn.close()

def save_birth_month(user_id, month):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO members (line_user_id, birth_month)
    VALUES (?, ?)
    ON CONFLICT(line_user_id)
    DO UPDATE SET birth_month=excluded.birth_month
    """, (user_id, month))
    conn.commit()
    conn.close()

# ===== 抓生日月 =====
def extract_birth_month(text):
    match = re.search(r'(1[0-2]|[1-9])\s*月', text)
    if match:
        return int(match.group(1))
    return None

# ===== Webhook =====
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.userId
    text = event.message.text

    month = extract_birth_month(text)

    if month:
        save_birth_month(user_id, month)
        reply = f"🎉 已幫你記錄生日月：{month} 月"
    else:
        reply = "請輸入你的生日月，例如：7月"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

