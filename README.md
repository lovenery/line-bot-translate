# line-bot-translate

## Build

```shell
# Install packages
pip install Flask line-bot-sdk gunicorn tinytag zhconv gspread authlib

# Or
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```shell
# Local
cp local.sh.example local.sh
./local.sh
ngrok http 5000
# Copy https://XXXXXXXX.ngrok.io/callback to Webhook URL.

# Remote
git remote add heroku https://git.heroku.com/[NAME].git # or heroku git:remote -a [NAME]
heroku config
heroku config:set LINE_CHANNEL_SECRET=
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=
heroku config:set YANDEX_API_KEY=
heroku config:set GOOGLE_CLIENT_SECRET="$(< client_secret.json)"
heroku config:set GOOGLE_SHEET_NAME=""
git push heroku master
heroku open
```

## Refs

- https://developers.line.me/
- https://developers.line.me/en/docs/messaging-api/reference/
- https://github.com/line/line-bot-sdk-python
- https://tech.yandex.com/translate/
- https://coreyward.svbtle.com/how-to-send-a-multiline-file-to-heroku-config
- https://github.com/burnash/gspread
