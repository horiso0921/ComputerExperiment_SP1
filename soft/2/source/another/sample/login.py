#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()

# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3

# データベースファイルのパスを設定
dbname = 'database1.db'
#dbname = ':memory:'

# テーブルの作成
con = sqlite3.connect(dbname)
cur = con.cursor()
create_table = 'create table if not exists users (name varchar(32),password int(16))'
cur.execute(create_table)
con.commit()
cur.close()
con.close()

def application(environ, start_response):

    #HTML(共通ヘッダ部分)
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>WSGI テスト</title>\n' \
           '<link rel="stylesheet" href="default.css">\n' \
           '</head>\n'
    #フォームデータ所得
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)
    if ('v1' not in form) or ('v2' not in form):
        html += '<body>\n' \
                '<div class="form1">\n' \
                '<form>\n' \
                'ユーザー名 <input type="text" name="v1"><br>\n' \
                'パスワード <input type="password" name="v2"><br>\n' \
                '<input type="submit" value="ログイン">\n' \
                '</form>\n' \
                '</div>\n' \
                '</body>\n'
    else:
        v1 = form.getvalue("v1", "0")
        v2 = form.getvalue("v2", "0")

        con = sqlite3.connect(dbname)
        cur = con.cursor()
        con.text_factory = str

        sql = 'SELECT count(*) from users where name = ? and password =?'
        import hashlib
        passwd = hashlib.md5(v2.encode('utf-8')).hexdigest()
        cur.execute(sql, [v1, passwd])
        result = cur.fetchall()


        if (result[0][0] == 0):
            html += '<body>\n' \
                    '<p>ログインに失敗しました．</p>\n' \
                    '<a href="/moge">ログインページへ戻る</a>\n' \
                    '</body>\n'

        else:
            sql = 'SELECT * from users where id = ? and pass = ?'

            html += '<body>\n' \
                    '<div class="ol1">\n' \
                    '<ol>\n'
            for row in cur.execute(sql, [v1, passwd]):
                html += '<li>' + row[0] + ',' + row[1] + '</li>\n'
            html += '</ol>\n' \
                    '</div>\n' \
                    '<a href="/hage">go</a>\n' \
                    '</body>\n'

        cur.close()
        con.close()


    html += '</html>\n'
    html = html.encode('utf-8')

    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))) ])
    return [html]

from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
