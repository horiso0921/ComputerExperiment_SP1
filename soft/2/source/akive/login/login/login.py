#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()
# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3
#password
import bcrypt


# データベースファイルのパスを設定
DBNAME = 'database.db'
# DBNAME = ':memory:'


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
a = \
"""
< body >
    <div class="form1">
    フォロー
<br>{0}</br>
    フォロワー
<br>{1}</br>
    
        </div>
< body >
""".format(flw,fl)
LOGIN_CONTENTS_HTML = \
"""
    <body>
        <div class="form1">
        <h1>ログイン</h1>
        <form>
            名前       （文字列） <input type="text" name="name"><br>
            パスワード　（文字列） <input type="password" name="pwd"><br>
            <input type="submit" name="login" value="ログイン">
        </form>
        </div>
    </body>
"""

SIGNUP_CONTENTS_HTML = \
"""
    <body>
        <div class="form2">
        <h1>新規登録</h1>
        <form>
            名前       （文字列） <input type="text" name="name"><br>
            パスワード　（文字列） <input type="password" name="pwd"><br>
            <input type="submit" name="signin" value="登録">
        </form>
        </div>
    </body>
"""

HOME_CONTENTS_HTML = \
"""
<p>Hellow homepage!!</p>
"""

FOOTER_HTML = \
"""
   <footer>
        <a href="/userpage?name{}">ページに戻る</a>
    </footer>
</html>
""".format(page)

ERROR_HTML = """<font color="red">{error}</font>"""


def db_init():
    # テーブルの作成
    con = sqlite3.connect(DBNAME)
    con.text_factory = str
    cur = con.cursor()
    create_table = 'create table if not exists users (name text, password text)'
    try:
        cur.execute(create_table)
        print("ok")
    except sqlite3.OperationalError:
        print("er")
        pass
    con.commit()
    cur.close()
    con.close()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_user(name):
    # データベース接続とカーソル生成
    con = sqlite3.connect(DBNAME)
    con.text_factory = str
    con.row_factory = dict_factory
    cur = con.cursor()
    sql = 'select * from users where name = ?'
    res = cur.execute(sql, (name,)).fetchone()
    print(res)

    cur.close()
    con.close()

    return res

def set_user(name, pwd):
    # データベース接続とカーソル生成
    con = sqlite3.connect(DBNAME)
    cur = con.cursor()
    sql = 'insert into users (name, password) values (?,?)'

    try:
        hashed_pwd = hash_pwd(pwd)
        print("hashed_pwd: {}".format(pwd))
        cur.execute(sql, (name, hashed_pwd))
    except Exception as e:
        print(str(e))
        return False

    con.commit()
    cur.close()
    con.close()

    return True

def hash_pwd(password, rounds=12):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds)).decode('utf8')

def check_pwd(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf8'), hashed_password.encode('utf8'))


def application(environ,start_response):
    error = None

    # HTML（共通ヘッダ部分）
    html = HEADER_HTML

    # フォームデータを取得
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)

    if ('signin' in form):
        # フォームデータから各フィールド値を取得
        name = form.getvalue("name", "0")
        pwd = form.getvalue("pwd", "0")

        # print("name: {}, pure_pwd: {}".format(name, pwd))

        res = get_user(name)
        print(res)

        if (res is not None):
            print("すでにユーザーが存在。ログイン画面へ遷移")
            error = "すでにユーザーが存在。ログイン画面へ遷移"
            html += LOGIN_CONTENTS_HTML
        
        else:
            if (set_user(name, pwd)):
                print("ユーザーの作成に成功")
                html += LOGIN_CONTENTS_HTML
            
            else:
                print("ユーザーの作成に失敗")
                error = "ユーザーの作成に失敗"
                html += SIGNUP_CONTENTS_HTML


    elif ('login' in form):
        name = form.getvalue("name", "0")
        pwd = form.getvalue("pwd", "0")

        # print("name: {}, pure_pwd: {}".format(name, pwd))

        res = get_user(name)
        print(res)

        if (res is not None):
            if (check_pwd(res["password"], pwd)):
                print("認証成功。")
                html += HOME_CONTENTS_HTML
            
            else:
                print("認証失敗。")
                error = "認証失敗。"
                html += LOGIN_CONTENTS_HTML

        else:
            print("ユーザーが存在しない。新規登録画面へ遷移")
            error = "ユーザーが存在しない。"
            html += SIGNUP_CONTENTS_HTML


    else:
        html += SIGNUP_CONTENTS_HTML

    if (error is not None):
        html += ERROR_HTML.format(error=error)
    html += FOOTER_HTML
    html = html.encode('utf-8')

    # レスポンス
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))) ])
    return [html]


# リファレンスWEBサーバを起動
#  ファイルを直接実行する（python test_wsgi.py）と，
#  リファレンスWEBサーバが起動し，localhost:8080 にアクセスすると
#  このサンプルの動作が確認できる
from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
    
