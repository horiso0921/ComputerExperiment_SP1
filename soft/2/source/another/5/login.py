#-*- coding:utf-8 -*-
import os, datetime, cgi
import StringIO
from wsgiref import util, simple_server
from xml.sax import saxutils
import topic
import sqlite3
import webbrowser
topic_class = topic.MessageBoard()

class LoginField(object):

    def __init__(self):
        ''' 初期化 '''

        # メッセージを保存するリストを定義
        self.messages = []


    def __call__(self, environ, start_response):
        ''' WSGI アプリケーション '''

        # リクエストメソッドを取得
        method = environ['REQUEST_METHOD']

        if method == 'GET':
            # GET の場合
            return self.listMessages(environ, start_response)

        elif method == 'POST':
            # POST の場合
            return self.addMessage(environ, start_response)

        else:
            # それ以外の場合は 501 を返す
            start_response('501 Not Implemented', [('Content-type', 'text/plain')])
            return 'Not Implemented'


    def listMessages(self, environ, start_response):
        ''' 一覧表示 '''

        fp = StringIO.StringIO()

        # ヘッダを出力
        fp.write(r'''<html>
<head><title>Login Field</title>
<meta http-equiv="Content-type" content="text/html; charset=utf-8">
</head>
<body>
''')
        
        # メッセージ数分繰り返し
        for msg in reversed(self.messages):

            esc = saxutils.escape

            tmp = {}

            # 入力を全てエスケープして出力
            for key, value in msg.iteritems():
                value = str(value)
                tmp[key] = str(esc(unicode(value, 'utf-8', 'ignore')))


            # メッセージの内容を書き出す
            fp.write('''<dl>
<dt>message</dt>
<dd>%(message)s</dd>
<hr /></dl>''' % tmp)

        # 書込み用フォームを出力
        fp.write('''<form action="%s" method="POST" AcceptEncoding="utf-8">
<dl>
<dt>name</dt>
<dd><input type="text" name="name"/></dd>
<dt>Password</dt>
<dd><input type="text" name="pasword"/></dd>
</dl>
<input type="submit" name="save" value="Post" />
</form>
</body></html>''' % util.request_uri(environ))



        # シーク位置を先頭にしておく
        fp.seek(0)

        start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
        return fp


    def addMessage(self, environ, start_response):
        ''' メッセージを追加する '''
        
        hage = 0
        # POST データを取得
        inpt = environ['wsgi.input']
        length = int(environ.get('CONTENT_LENGTH', 0))
        dbname = 'user.db'
        con = sqlite3.connect(dbname)
        cur = con.cursor()

        # 取得したデータをパースして辞書オブジェクトに変換
        query = dict(cgi.parse_qsl(inpt.read(length)))
        print(query)
        # POST メッセージを保存
        n = cur.execute('SELECT * FROM users WHERE name = ?',(query['name'],))
        if len(n.fetchall()) != 0:
            cur.close()
            cur = con.cursor()
            m = cur.execute('SELECT * FROM users WHERE name = ? AND pasword = ?',(query["name"],query['pasword']))
            cur.close()
            if (len(m.fetchall())!= 0):
                msg = {'message':"Login Success!"
                       }
                #start_response =topic_class.listMessages(environ,start_response)[1]
            
                hage +=1
            else:
                msg = {'message':"pasword is wrong"
                       }
                cur.close()
        else:
            cur = con.cursor()
            user = (query['name'],query['pasword'])
            cur.execute('insert into users(name,pasword)VALUES(?,?)',user)
            con.commit()
            msg = {'message':"You are new User!"
                       }
            print(msg)
            #webbrowser.open("index.html")
            cur.close()
        con.close()
        self.messages.append(msg)

        if (hage== 0):
            # リダイレクトを行う
            start_response('303 See Other', [('Content-type', 'text/plain'),
                                             ('Location', util.request_uri(environ))])
        return ''



from wsgiref import simple_server

application = LoginField()


if __name__ == '__main__':

    srv = simple_server.make_server('', 8081, application)

    srv.serve_forever()

    
