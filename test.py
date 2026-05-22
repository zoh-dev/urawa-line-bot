import requests
import re
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
from flask import Flask, request
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.messaging import PushMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

app = Flask(__name__)

# ここに自分の情報を入れる
CHANNEL_ACCESS_TOKEN = "jUiJ/e8soKu5g7MEB0yfJLz/lwM2gTKdBuE1OUeC5HEz70bGX6OhWj0w+nAC98izYLmWCt0ZZdbwmRTqeq7cnuDrw4HsGr5sIocthMnHD+xe++0PtOQ+g3TG3NShib66pr04AWCv+AIGZ7AjuRR18QdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "3e49200aeb045a4d8fae30677f81aad3"

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text

    if "次の試合" in user_text:
        reply_text = "次の浦和レッズ試合日: 2026/05/22"

    elif "順位" in user_text:
        reply_text = "浦和レッズ現在順位: J1リーグ 4位"

    elif "ニュース" in user_text:
        reply_text = "浦和レッズ最新ニュース: 新加入選手の発表がありました"

    else:
        reply_text = event.source.user_id

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

def send_daily_notice():
    tomorrow = "2026/05/22"   # テスト用。あとで自動化する

    if tomorrow == "2026/05/22":
        text = "明日は浦和レッズ試合です！"
    else:
        return

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        line_bot_api.push_message(
            PushMessageRequest(
                to="U0b2db964ff27c4ec92639a170257c74f",
                messages=[TextMessage(text=text)]
            )
        )

schedule.every().day.at("21:44").do(send_daily_notice)


if __name__ == "__main__":
    import threading

    thread = threading.Thread(target=lambda: app.run(port=5000))
    thread.start()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    import threading

    thread = threading.Thread(target=lambda: app.run(port=5000))
    thread.start()

    print("ここ通った")
    send_daily_notice()

    while True:
        schedule.run_pending()
        time.sleep(1)