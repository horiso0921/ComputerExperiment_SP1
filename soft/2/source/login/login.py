#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("/var/www/cgi-bin")

# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()
# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3
#password HASH化用
#import bcrypt
import urllib.request
from session import Session
from user import User

# login
def login(environ, start_response):

    # html
    HEADER_HTML = \
    """
    <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>Login</title>
            <link rel="stylesheet" href="default.css">
        </head>
    """
    cookie_str = environ.get('HTTP_COOKIE')

    try:
        Session(cookie_str)
        response_header = [('Location','/userpage')]
        start_response('301 Moved', response_header)
        return ""
        
    except:
        pass
    #login_pageのhtml
    LOGIN_CONTENTS_HTML = \
    """
        <body>
            <div class="form1">
            <h1>ログイン</h1>
            <form method="POST" action="login">
                名前       （文字列） <input type="text" name="name"><br>
                パスワード（文字列） <input type="password" name="pwd"><br>
                <input type="submit" name="login" value="ログイン">
                <input type="submit" name="signin" value="新規登録">
            </form>
            </div>
        </body>
    """

    #ログインに成功した際のコネクション(未解決)
    NEXT_CONTENTS_HTML = \
    """
        <p>ログイン成功!!</p>
        <footer>
            <a href="/userpage">userpage</a>
        </footer>
    """

    # </html>
    FOOTER_HTML = \
    """
    </html>
    """

    # エラー用
    ERROR_HTML = """<font color="red">{error}</font>"""

        
    # クエリの構文解析
    def parse_query(query):
        name = ''
        pwd = ''
        method = ''

        for param, value in query:
            if param == 'name':
                name = value
            elif param == 'pwd':
                pwd = value
            elif param == 'login':
                method = param
            elif param == 'signin':
                method = param
    
        errors = []
        if name == '':
            errors.append('ユーザー名の入力がありません。')
        if pwd == '':
            errors.append('パスワードの入力がありません。')
        if method == '':
            errors.append('予期せぬエラーが発生しました')
    
        return name, pwd, method, errors

    errors = []
    login_session = None

    # HTML（共通ヘッダ部分）
    html = HEADER_HTML

    #リクエストを読み取る
    request = environ.get('REQUEST_METHOD')

    if request == "POST":
        wsgi_input = environ['wsgi.input']
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        query = cgi.parse_qsl(wsgi_input.read(content_length).decode('UTF-8'))
        print(query)
        name, pwd, method, errors = parse_query(query)
        
        # errorsが空の場合はすべての入力がある
        if errors == []:
            

            
            # loginボタンが押された場合login
            # 失敗の場合はerrorを返す
            if method == 'login':
                login_session = Session.login(name, pwd)

                if login_session != None:
                    print(!")
                    html += NEXT_CONTENTS_HTML

                else:
                    errors.append("ログインエラー:ユーザーがいないかパスワードが異なります")
                    html += LOGIN_CONTENTS_HTML

            # 新規登録ボタンが押された場合
            # 例外は新規作成できず
            if method == 'signin':

                try:
                    User.CreateNewUser(name, pwd)
                    print("ユーザーの作成に成功")

                except:
                    errors.append("ユーザーの作成に失敗")

                html += LOGIN_CONTENTS_HTML

        else:
            html += LOGIN_CONTENTS_HTML

        # エラー内容をprint
        for error in errors:
            print(error)

        if errors != []:
            html += ERROR_HTML.format(error="".join(errors))

    else:
        html += LOGIN_CONTENTS_HTML

    html += FOOTER_HTML

    html = html.encode('utf-8')

    # cookieチェック用
    # loginには関係なし
    cookie_str = environ.get('HTTP_COOKIE')
    if cookie_str:
        cookies = cookie_str.split(";")
        for cookie in cookies:
            if "token" in cookie:
                dummy, token = cookie.split("=")
                print(token)

    # レスポンス
    if login_session != None:
        response_header = [('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(html))), login_session]

    else:
        response_header = [('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(html)))]

    start_response('200 OK', response_header)
    return [html]

 

# リファレンスWEBサーバを起動
#  ファイルを直接実行する（python login.py）と，
#  リファレンスWEBサーバが起動し，localhost:8080 にアクセスすると
#  このサンプルの動作が確認できる
from wsgiref import simple_server

if __name__ == '__main__':
    server = simple_server.make_server('', 8080, login)
    server.serve_forever()
    
