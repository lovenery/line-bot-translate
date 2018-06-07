from datetime import datetime
from os import environ
from json import loads
from authlib.client import AssertionSession
import gspread

"""
gspread:
https://youtu.be/vISRn5qFrkM
https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption

oauth issues:
https://github.com/google/oauth2client/issues/735
https://www.reddit.com/r/learnpython/comments/8elu5a/google_sheets_api_dilemma_googleauth_and_gspread/
    https://github.com/burnash/gspread/issues/529

oauth solution:
https://www.reddit.com/r/Python/comments/8kzra5/how_to_use_gspread_without_oauth2client/?st=JHG7OFKZ&sh=051ca8af
    https://blog.authlib.org/2018/authlib-for-gspread
"""

def create_assertion_session(scopes, subject=None):
    # with open(conf_file, 'r') as f:
    #     conf = json.load(f)
    conf = loads(environ['GOOGLE_CLIENT_SECRET'])

    token_url = conf['token_uri']
    issuer = conf['client_email']
    key = conf['private_key']
    key_id = conf.get('private_key_id')

    header = {'alg': 'RS256'}
    if key_id:
        header['kid'] = key_id

    # Google puts scope in payload
    claims = {'scope': ' '.join(scopes)}
    return AssertionSession(
        grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
        token_url=token_url,
        issuer=issuer,
        audience=token_url,
        claims=claims,
        subject=subject,
        key=key,
        header=header,
    )

def append_google_sheet(profile_dict, msg):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    session = create_assertion_session(scope)

    client = gspread.Client(None, session)
    sheet = client.open(environ['GOOGLE_SHEET_NAME']).sheet1

    # content = sheet.get_all_values()
    # print(content)

    now = datetime.now()
    row = [str(now), profile_dict['display_name'], profile_dict['picture_url'], profile_dict['status_message'], profile_dict['user_id'], msg]
    sheet.append_row(values=row, value_input_option='USER_ENTERED')

if __name__ == '__main__':
    profile_dict = {
        'display_name': 'test_name',
        'picture_url': 'https://www.google.com',
        'status_message': 'testing',
        'user_id': '123'
    }
    append_google_sheet(profile_dict, 'apple')
