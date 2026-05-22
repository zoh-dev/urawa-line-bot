import requests
from bs4 import BeautifulSoup
import re
import schedule
import time
from datetime import datetime, timedelta
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
    print("callbackきた")

    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    print(body)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(e)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text

    if "次の試合" in user_text:
        with open("match_data.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        if lines:
            first_line = lines[0].strip()
            date, opponent, place = first_line.split(",")

            reply_text = f"""次の試合情報
対戦相手：{opponent}
日時：{date}
場所：{place}"""
        else:
            reply_text = "試合情報が取得できませんでした"

    elif "今日試合" in user_text:
        today = datetime.today().strftime("%Y/%m/%d")

        with open("match_data.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        found = False
        for line in lines:
            date, opponent, place = line.strip().split(",")
            if date == today:
                reply_text = f"""今日は試合があります
対戦相手：{opponent}
場所：{place}"""
                found = True
                break

        if not found:
            reply_text = "今日は試合ありません"

    else:
        with open("user_id.txt", "a", encoding="utf-8") as f:
            f.write(event.source.user_id + "\n")

        reply_text = "浦和レッズ通知BOTです！\n「次の試合」と送ると試合情報を表示します。"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

def send_daily_notice():
    print("通知関数スタート")

    tomorrow = (datetime.today() + timedelta(days=2)).strftime("%Y/%m/%d")

    with open("user_id.txt", "r", encoding="utf-8") as f:
        user_ids = f.readlines()

    with open("match_data.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        date, opponent, place = line.strip().split(",")

        if date == tomorrow:
            message = f"""明日は浦和レッズ試合です！
対戦相手：{opponent}
場所：{place}
日付：{date}"""

            for user_id in user_ids:
                user_id = user_id.strip()

                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)

                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=user_id,
                            messages=[TextMessage(text=message)]
                        )
                    )

                print(f"{user_id} に通知送信完了")

            break

schedule.every().day.at("22:30").do(send_daily_notice)


if __name__ == "__main__":
    import threading

    thread = threading.Thread(target=lambda: app.run(port=5000))
    thread.start()

    send_daily_notice()

    while True:
        schedule.run_pending()
        time.sleep(1)

   