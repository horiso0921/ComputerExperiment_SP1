#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb
cgitb.enable()

import sqlite3

dbname = '/tmp/userinfo.db'
#dbname = ':memory:'

con = sqlite3.connect(dbname)
cur = con.cursor()
create_table = 'CREATE TABLE if not exists users (id varchar(64), pass varchar(64))'
cur.execute(create_table)
con.commit()
cur.close()
con.close()

def application(environ,start_response):
    html = '<!DOCTYPE html>\n' \
           '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>ユーザー登録ページ</title>\n' \
           '<link rel="stylesheet" href="default.css">\n' \
           '</head>\n'

    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)
    if ('v1' not in form) or ('v2' not in form):
        html += '<body>\n' \
                '<div class="form1">\n' \
                '<form>\n' \
                'ユーザー名 <input type="text" name="v1"><br>\n' \
                'パスワード <input type="password" name="v2", placeholder="8文字以上"><br>\n' \
                '<input type="submit" value="登録">\n' \
                '</form>\n' \
                '</div>\n' \
                '<a href="http://icesc18/moge">ログインページはこちら</a>\n' \
                '</body>\n'
    else:
        v1 = form.getvalue("v1", "0")
        v2 = form.getvalue("v2", "0")
        l1 = len(v1)
        l2 = len(v2)

        if (l1 == 0) or (l2 == 0):
            html += '<body>\n' \
                    '<p>入力されていない箇所があります．</p>\n' \
                    '<a href="/hoge">ユーザー登録ページへ戻る</a>\n' \
                    '</body>\n'

        elif (l2 < 8):
            html += '<body>\n' \
                    '<p>パスワードが8文字未満です．</p>\n' \
                    '<a href="/hoge">ユーザー登録ページへ戻る</a>\n' \
                    '</body>\n'

        else:
            con = sqlite3.connect(dbname)
            cur = con.cursor()
            con.text_factory = str

            sql = 'SELECT count(id) from users where id = ?'
            cur.execute(sql, [v1])
            result = cur.fetchall()

            if (result[0][0] != 0):
                html += '<body>\n' \
                        '<p>このユーザー名は既に使用されています．</p>\n' \
                        '<a href="/hoge">ユーザー登録ページへ戻る</a>\n' \
                        '</body>\n'

            else:
                sql = 'INSERT into users (id, pass) values (?,?)'
                import hashlib
                passwd = hashlib.md5(v2.encode('utf-8')).hexdigest()
                cur.execute(sql, (v1,passwd))
                con.commit()

                html += '<body>\n' \
                        '<div class="hj1">\n' \
                        '<p>ユーザー名 : ' + str(v1) + '</p>\n' \
                        '<p>パスワード : ' + str(v2) + '</p>\n' \
                        '<p>にて登録しました．</p>\n' \
                        '</div>\n' \
                        '<a href="http://icesc18/moge">ログインページはこちら</a>\n' \
                        '</body>\n'

            cur.close()
            con.close()

    html += '</html>\n'
    #html = html.encode('utf-8')

    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))) ])
    return [html]

from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
