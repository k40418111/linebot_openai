from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# Initialize message counter
message_counter = 0

# 讀取計數器的值
def load_counter():
    try:
        with open('counter.txt', 'r') as f:
            return int(f.read())
    except FileNotFoundError:
        return 0

# 儲存計數器的值
def save_counter(counter):
    with open('counter.txt', 'w') as f:
        f.write(str(counter))

# 載入計數器
message_counter = load_counter()

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global message_counter  # 告訴 Python 使用全域變數
    text1=event.message.text
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content":"你現在回答問題時會隨時講冷笑話，最後都會加上 這個笑話讓人冷峻不禁"},
            {"role": "user", "content": text1}
        ],
        model="gpt-4o-mini-2024-07-18",
        temperature = 0.5,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
    except:
        ret = '發生錯誤！'
        
    # 增加計數器
    message_counter += 1
    save_counter(message_counter)  # 儲存新的計數值
    print(f"OpenAI 已回應 {message_counter} 次。")  # 調試訊息
    
    # 回覆訊息並包含計數
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{ret}\n\n累積訊息次數: {message_counter}"))

if __name__ == '__main__':
    app.run()
