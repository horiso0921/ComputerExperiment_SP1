#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()

# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3

# データベースファイルのパスを設定
dbname2 = 'example.db'

# テーブルの作成
con = sqlite3.connect(dbname2)
cur = con.cursor()
create_table = 'CREATE TABLE IF NOT EXISTS users10(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)'
cur.execute(create_table)
con.commit()
cur.close()
con.close()

def register(cur,con,v1,v2):
    username = v1
    password = v2
    html = ""
    #登録済のユーザー名でないかを確認
    index = cur.execute('SELECT * FROM users10')
    flag = True
    for row in index:
        if username == row[1]:
            html += '<li>' + 'そのユーザー名は登録済みです' + '</li>\n'
            html += '</ol>\n' \
                '</div>\n' \
                '<a href="/">登録ページに戻る</a>\n' \
                '</body>\n'
            #return "a"
            flag = False
            break
    if flag==True:
        #データの挿入
        ins_str = 'INSERT INTO users10(username, password) VALUES(?, ?)'
        con.execute(ins_str, (username,password))

        #挿入した結果を保存（コミット）する
        con.commit()
        '''
        # SQL文の実行とその結果のHTML形式への変換
        html += '<body>\n' \
            '<div class="ol1">\n' \
            '<ol>\n'
        '''
        #登録後の表示'
        html += '</ol>\n' \
            '</div>\n' \
            '<a href="/">登録ページに戻る</a>\n' \
            '</body>\n'
    return html

def check(cur,v1,v2):
    html = ""
    rogin = 0
    username = v1
    password = v2
    index = cur.execute('SELECT * FROM users10')
    for row in index:
        if username == row[1]:
            if password == row[2]:
                rogin = 1
                userID = row[0]
                html += '<li>' + 'ログインしました' + '</li>\n'
                return html
            else:
                html += '<li>' + 'パスワードが違います' + '</li>\n'
                html += '</ol>\n' \
                    '</div>\n' \
                    '<a href="/">登録ページに戻る</a>\n' \
                    '</body>\n'
                return html

    if rogin == 0:
        html += '<li>' + 'そのユーザー名は登録されていません' + '</li>\n'
        html += '</ol>\n' \
              '</div>\n' \
              '<a href="/">登録ページに戻る</a>\n' \
              '</body>\n'
        return html


def application(environ,start_response):
    # HTML（共通ヘッダ部分）
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>青空文庫</title>\n' \
           '<link rel="stylesheet" href="default.css">\n' \
           '</head>\n'

    # フォームデータを取得
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)
    if ('v1' not in form) or ('v2' not in form):
        # 入力フォームの内容が空の場合（初めてページを開いた場合も含む）

        # HTML（入力フォーム部分）
        html += '<body>\n' \
                '<div class="form1">\n' \
                '<form>\n' \
                'username  <input type="text" name="v1"><br>\n' \
                'password  <input type="text" name="v2"><br>\n' \
                '新規登録ですか y/n  <input type="text" name="v3"><br>\n' \
                '<input type="submit"">' \
                '</form>\n' \
                '</div>\n' \
                '</body>\n'

    else:
        # 入力フォームの内容が空でない場合

        # フォームデータから各フィールド値を取得
        v1 = form.getvalue("v1", "0")
        v2 = form.getvalue("v2", "0")
        v3 = form.getvalue("v3", "0")


        # データベース接続とカーソル生成
        con = sqlite3.connect(dbname2)
        cur = con.cursor()
        con2 = sqlite3.connect('example2.db')
        cur2 = con2.cursor()

        v1 = str(v1)
        v2 = str(v2)

        if v3 == "y":
            html += register(cur,con,v1,v2)
        elif v3 == "n":
            html += check(cur,v1,v2)
        else:
            html = 'a'

        # カーソルと接続を閉じる
        cur.close()
        con.close()

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
    b = application
    server = simple_server.make_server('', 8080, b)
    server.serve_forever()
