import os
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


CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

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
            date, weekday, match_time, opponent, place = first_line.split(",")

            reply_text = f"""次の試合情報
対戦相手：{opponent}
日付：{date}（{weekday}）
試合時間：{match_time}
場所：{place}"""
        else:
            reply_text = "試合情報が取得できませんでした"

    elif "今日試合" in user_text:
        today = datetime.today().strftime("%Y/%m/%d")

        with open("match_data.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        found = False
        for line in lines:
            date, weekday, match_time, opponent, place = line.strip().split(",")
            if date == today:
                reply_text = f"""今日は試合があります
対戦相手：{opponent}
日付：{date}（{weekday}）
試合時間：{match_time}
場所：{place}"""
                found = True
                break

        if not found:
            reply_text = "今日は試合ありません"

    else:
        with open("user_id.txt", "r", encoding="utf-8") as f:
            saved_ids = f.read().splitlines()

        if event.source.user_id not in saved_ids:
            with open("user_id.txt", "a", encoding="utf-8") as f:
                f.write(event.source.user_id + "\n")

        reply_text = f"""浦和レッズ通知BOTです⚽

        「次の試合」
        → 次回試合情報

        「今日試合」
        → 今日の試合確認"""

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

    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y/%m/%d")

    with open("user_id.txt", "r", encoding="utf-8") as f:
        user_ids = f.readlines()

    with open("match_data.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        date, weekday, match_time, opponent, place = line.strip().split(",")

        if date == tomorrow:
            message = f"""明日は浦和レッズ試合です！
対戦相手：{opponent}
日時：{date}（{weekday}）
試合時間：{match_time}
場所：{place}"""

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

    while True:
        schedule.run_pending()
        time.sleep(1)

   