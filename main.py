from flask import Flask, request, abort
from os import environ, path
import requests
from tinytag import TinyTag
from zhconv import convert
from helper import database
import threading

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
from linebot.exceptions import LineBotApiError

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
    base_dir = path.abspath(path.dirname(__file__))
    relative_dir = 'static/uploads/'
    file_name = event.message.id
    file_extension = '.mp3'

    file_rel_path = path.join(relative_dir, file_name + file_extension)
    file_abs_path = path.join(base_dir, file_rel_path)
    url_path = path.join('https://' + request.host, file_rel_path)

    msg = str(event.message.text)
    url = 'https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&q={}'.format(msg)
    res = requests.get(url)
    with open(file_abs_path, 'wb') as fd:
        for chunk in res.iter_content():
            fd.write(chunk)

    tiny_tag = TinyTag.get(file_abs_path)
    # print('It is %f milliseconds long.' % (tiny_tag.duration * 1000))

    params = {
        'key': environ['YANDEX_API_KEY'],
        'text': msg,
        'lang': 'zh',
    }
    res = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate', params=params)
    yandex = res.json()
    yandex_text = convert(yandex['text'][0], 'zh-tw')

    try:
        line_bot_api.reply_message(event.reply_token, [
            AudioSendMessage(
                original_content_url=url_path,
                duration= tiny_tag.duration * 1000, #milliseconds
            ),
            TextSendMessage(text='你說：「'+event.message.text+'」。'),
            TextSendMessage(text='點這裡聽聽看：{}'.format(url_path)),
            TextSendMessage(text='意思是：{}'.format(yandex_text)),
        ])
    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)

    if not environ.get('GOOGLE_CLIENT_SECRET') or not environ.get('GOOGLE_SHEET_NAME'):
        app.logger.info("GOOGLE_CLIENT_SECRET or GOOGLE_SHEET_NAME was not found or empty.")
    else:
        profile = line_bot_api.get_profile(event.source.user_id)
        kwargs_dict = {
            'profile_dict': {
                'display_name': profile.display_name,
                'picture_url': profile.picture_url,
                'status_message': profile.status_message,
                'user_id': profile.user_id
            },
            'msg': msg
        }
        db_thread = threading.Thread(target=database.append_google_sheet, kwargs=kwargs_dict)
        db_thread.start()

if __name__ == '__main__':
    app.run(port = int(environ['PORT']))
