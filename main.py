from flask import Flask, request, abort
from os import environ

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi(environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(environ['LINE_CHANNEL_SECRET'])

@app.route('/')
def index():
    return 'It works!'

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info('X-Line-Signature: ' + signature)
    app.logger.info('Request body: ' + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error('LINE_CHANNEL_SECRET Error.')
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='你說：「'+event.message.text+'」。'))

if __name__ == '__main__':
    app.run(port = int(environ['PORT']))
