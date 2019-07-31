#!/usr/bin/env python
# -*- coding: utf-8 -*-
# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()

# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3
#データベースへのアクセス
import sys
sys.path.append("/var/www/cgi-bin")
from session import Session
from user import User



def application(environ, start_response):

    # HTML（共通ヘッダ部分）
    html = \
    """
    <html lang="ja">
        <head>
        <link rel="stylesheet" href="default.css">
        <title>follow_follower_page</title>
        <meta charset="UTF-8">


        </style>
      </head>
      """

    # GETやPOSTのクエリの辞書
    request = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    # 指定されたページのユーザ
    logging_user = Session(environ['HTTP_COOKIE']).user
    page_user = User(request.getvalue('user', logging_user.name))
    follow_list = page_user.following()
    follower_list = page_user.followers()

    fwl = ""
    fwel = ""
    for user in follow_list:
        fwl += '<a href="userpage?user={}">{}</a><br/>'.format(user.name, user.name)
    for user in follower_list:
        fwel += '<a href="userpage?user={}">{}</a><br/>'.format(user.name, user.name)

    html += \
"""
<body>
    <div class="form1">
    フォロー
<p>{0}</p>
    フォロワー
<p>{1}</p>

        </div>
</body>
""".format(fwl,fwel)


    html  += \
"""
   <footer>
        <a href="userpage?user={}">ページに戻る</a>
    </footer>
</html>
""".format(page_user.name)

    start_response('200 OK', [('Content-type', 'text/html')])

    return [html.encode('utf-8')]


from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
    db_init()
