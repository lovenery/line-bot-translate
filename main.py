from flask import Flask, request, abort
from os import environ, path
import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    AudioSendMessage
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
    msg = str(event.message.text)

    base_dir = path.abspath(path.dirname(__file__))
    relative_path = 'static/uploads/'
    file_name = event.message.id
    file_extension = '.mp3'
    file_path = relative_path + file_name + file_extension

    url = 'https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&q={}'.format(msg)
    res = requests.get(url)
    with open(path.join(base_dir, file_path), 'wb') as fd:
        for chunk in res.iter_content():
            fd.write(chunk)

    url_path = path.join('https://' + request.host, file_path)
    audio_message = AudioSendMessage(
        original_content_url=url_path,
        duration=240000,
    )

    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='你說：「'+event.message.text+'」。'),
            audio_message,
        )
    except Exception as e:
        print('Error:')
        print(e)

if __name__ == '__main__':
    app.run(port = int(environ['PORT']))
