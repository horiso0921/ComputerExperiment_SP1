#! /usr/bin/env python3
#-*- coding: utf-8 -*-

# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()
#sqlite3（SQLサーバ）モジュールをインポート
import sqlite3

# データベースファイルのパスを設定
#dbname = '/tmp/database.db'
#dbname = '/home/sshunya/jikken/kadai6.db'
#dbname = '/mdhome/home5/nt8157285/htmltest/kadai6.db'
#dbname = '/mdhome/home1/sf8827071/jikken/kadai6.db'
dbname = 'kadai6.db'

#dbname = ':memory:'

# テーブルの作成
con = sqlite3.connect(dbname)
cur = con.cursor()
create_table = 'create table if not exists users (id int, pass varchar(64))'
cur.execute(create_table)
create_table = 'create table if not exists hyouka (uID int,bID int,hyouka int)'
cur.execute(create_table)
create_table = 'create table if not exists kidoku (uID int,bID int)'
cur.execute(create_table)
create_table = 'create table if not exists aozora (bookID int,title text,author text)'
con.commit()
cur.close()
con.close()

def ninsyou(html,v1,v2):
    #ろぐいん処理

    # データベース接続とカーソル生成
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str
    
    #SQL文（select）の作成
    sql = 'select * from users' 

    #ログインが成功したか判別するフラグ
    flg_login = False

    #SQL文の実行
    for row in cur.execute(sql):
        if( v1 == str(row[0]) ) and ( v2  == row[1]):
            #ログイン情報がDBと一致したらTrue
            flg_login = True


    if(flg_login == True):
        #Cookie
        uID = 'uID='+v1
        response_header = [('Content-Type', 'text/html; charset=utf-8'),('Set-Cookie',uID)]
        html += '<body>\n' \
            '<div class="form1">\n' \
            '<div class="form-wrapper">\n'\
            '<form>\n' \
            'ログイン成功<br>\n' \
            '<div class="button-panel">\n'\
            '<button class="button" type="submit" name="home" value="1">ホーム</button><br>\n' \
            '</form>\n' \
            '</div>\n' \
            '</div>\n'\
            '</body>\n'
    else:
        uID = 'uID=0'
        response_header = [('Content-Type', 'text/html; charset=utf-8'),('Set-Cookie',uID)]
        html += '<body>\n' \
            '<div class="form1">\n' \
            '<div class="form-wrapper">\n'\
            '<form>\n' \
            'ログイン失敗<br>\n' \
            '<div class="button-panel">\n'\
            '<a class="button" href="/">ログインページに戻る</a>\n' \
            '</form>\n' \
            '</div>\n'\
            '</div>\n' \
            '</div>\n'\
            '</body>\n'

    return html,response_header

def kensaku(html,v1,v2,form,val):
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str
    vk = form.getvalue("kensaku","0")
    uID = int(val)
    if (vk == '2'):
        title = form.getlist("title")
        sql = 'insert into kidoku values(?,?)'
        for i in range(len(title)):
            cur.execute(sql,(int(uID),int(title[i])))
            con.commit()
    html += '<body>\n' \
            '<div class="form1">\n' \
            '<form>\n' \
            '書名検索 <input type="text" name="v1"><br>\n' \
            '作家検索 <input type="text" name="v2"><br>\n' \
            '<button type="submit" name="kensaku" value="1">検索</button><br>\n' 
    if (len(v1) != 0)and(len(v2) == 0):
        html += '検索結果<br>\n'
        #書名検索 検索結果html
           
        sql2 = 'select aozora.title,aozora.author,aozora.bookID from aozora where title = ? or title = ?'
       
        for row in cur.execute(sql2,(v1,v1)):#cur.execute(str,(,)) no katati de kaku
            html += '<li>' + str(row[0]) + ',' + str(row[1]) + ',既読:' + '<input type="radio" name="title" value="' + str(row[2])+'"> </li>\n'
            #編集ここまで

    elif (len(v2) != 0)and(len(v1) == 0):
        html += '検索結果<br>\n'
        #作家検索 検索結果html
           
        sql2 = 'select aozora.title,aozora.author,aozora.bookID from aozora where author = ? or author = ?'
       
        for row in cur.execute(sql2,(v2,v2)):#cur.execute(str,(,)) no katati de kaku
            html += '<li>' + str(row[0]) + ',' + str(row[1]) + ',既読:' + '<input type="radio" name="title" value="' + str(row[2])+'"> </li>\n'
            #編集ここまde

    elif (len(v1) != 0)and(len(v2) != 0):
        html += '検索結果<br>\n'
        #同時検索 検索結果html    
           
        sql2 = 'select aozora.title,aozora.author,aozora.bookID from aozora where title = ? or title = ? or author = ? or author = ?'
       
        for row in cur.execute(sql2,(v1,v1,v2,v2)):#cur.execute(str,(,)) no katati de kaku
            html += '<li>' + str(row[0]) + ',' + str(row[1]) + ',既読:' + '<input type="radio" name="title" value="' + str(row[2])+'"> </li>\n'
            #編集ここまで


    html += '<button type="submit" name="home" value="1">ホーム</button><br>\n' \
            '<button type="submit" name="kensaku" value="2">既読登録</button><br>\n' \
            '</form>\n' \
            '</div>\n' \
            '</body>\n'
    cur.close()
    con.close()
    return html

def kidoku(html,form,val):
    uID = int(val)#Cookieからもらう
    
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    cur2 = con.cursor()
    con.text_factory = str
    vk = form.getvalue("kidoku", "0")
    sql = 'select aozora.bookID,aozora.title,aozora.author from kidoku left outer join aozora on kidoku.bID = aozora.bookID where uID = ?'
    sql2 = 'insert into hyouka values(?,?,?)'
    html += '<body>\n' \
            '<div class="form1">\n' \
            '<form>\n'

    for row in cur.execute(sql,(int(uID),)):#cur.execute(str,(,)) no katati de kaku
        html += '<li>' + str(row[1]) + ',' + str(row[2]) + '<select name="'\
                + str(row[0]) + '">\n'\
                '<option value="-1">評価なし</option>\n'\
                '<option value="1">1</option>\n'\
                '<option value="2">2</option>\n'\
                '<option value="3">3</option>\n'\
                '</select></li><br>\n'
        if(vk == '2'):
            vbi = form.getvalue(str(row[0]),"0")
            if(vbi != '-1'):
                #html += 'faaaa'
                cur2.execute(sql2,(int(uID),int(row[0]),int(vbi)))
                con.commit()
    
    html += '<button type="submit" name="home" value="1">ホーム</button>\n' \
            '<button type="submit" name="kidoku" value="2">評価登録</button><br>\n' \
            '</form>\n' \
            '</div>\n' \
            '</body>\n'
    cur.close()
    con.close()
    return html
    
def hyouka(html,val):
    uID = int(val)# Cookieからもらう
        
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str
    # sql = 'select bID,hyouka from hyouka where uID = ?'        
    sql2 = 'select hyouka.hyouka,aozora.title,aozora.author from hyouka left outer join aozora on hyouka.bID = aozora.bookID where uID = ?'
    html += '<body>\n' \
            '<div class="form1">\n' \
            '<form>\n'
    for row in cur.execute(sql2,(int(uID),)):#cur.execute(str,(,)) no katati de kaku
        html += '<li>' + str(row[1]) + ',' + str(row[2]) + ',評価：' + str(row[0]) + '</li>\n'
    html += '<button type="submit" name="home" value="1">ホーム</button><br>\n' \
            '</form>\n' \
            '</div>\n' \
            '</body>\n'

    cur.close()
    con.close()
    return html

def regist(html,v1,v2):
        # データベース接続とカーソル生成
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        con.text_factory = str
        # SQL文（insert）の作成と実行
        sql = 'insert into users (id, pass) values (?,?)'
        cur.execute(sql, (int(v1),v2))
        con.commit()
        # SQL文（select）の作成
        sql = 'select * from users'
        # SQL文の実行とその結果のHTML形式への変換
        html += '<body>\n' \
                '<div class="ol1">\n' \
                '<ol>\n'
        for row in cur.execute(sql):
            html += '<li>' + str(row[0]) + ',' + row[1] + '</li>\n'
        html += '</ol>\n' \
                '</div>\n' \
                '<a href="/">ログインページに戻る</a>\n' \
                '</body>\n'
        # カーソルと接続を閉じる
        cur.close()
        con.close()
        return html

def login(html):
        # HTML（入力フォーム部分）
        html += '<body>\n' \
                '<div class="form1">\n' \
                '<form>\n'\
                '<div class="form-wrapper">\n'\
                '    <div class="form-item">\n'\
                '    <label for="ID"></label>\n'\
                '    <input type="ID" name="v1"  placeholder="ID"></input>\n'\
                '    </div>\n'\
                '   <div class="form-item">\n'\
                '    <label for="password"></label>\n'\
                '    <input type="password" name="v2" placeholder="Password"></input>\n'\
                '    </div>\n'\
                '    <button type="submit" name="login">ログイン</button>\n'\
                '    <button type="submit" name="account" >アカウント登録</button>\n'\
                '</form>\n'\
                '</div>\n'\
                '</div>\n'\
                '</form>\n' \
                '</div>\n' \
                '</body>\n'
        return html

def account(html):
    html += '<body>\n' \
            '<div class="form1">\n' \
                '<form>\n'\
                '<div class="form-wrapper">\n'\
                '    <div class="form-item">\n'\
                '    <label for="ID"></label>\n'\
                '    <input type="ID" name="v1" placeholder="ID"></input>\n'\
                '    </div>\n'\
                '   <div class="form-item">\n'\
                '    <label for="password"></label>\n'\
                '    <input type="password" name="v2" placeholder="Password"></input>\n'\
                '    </div>\n'\
                '    <button type="submit" name="regist">Regist</button>\n'\
                '</div>\n'\
                '</form>\n'\
            '</div>\n' \
            '</body>\n'
    return html

def home(html):
        html += '<body>\n' \
                '<div class="form1">\n' \
                '<form>\n' \
                '<button type="submit" name="kensaku" value="1">検索</button><br>\n' \
                '<button type="submit" name="kidoku" value="1">既読</button><br>\n' \
                '<button type="submit" name="hyouka" value="1">評価</button><br>\n' \
                '</form>\n' \
                '</div>\n' \
                '</body>\n'
        return html
        

def application(environ,start_response):
    # HTML（共通ヘッダ部分）
    response_header = [('Content-Type', 'text/html; charset=utf-8')]
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>あおぞら検索</title>\n' \
            '<style type="text/css">\n' \
            'body {font-size: 20px} \n' \
            '@import url(https://fonts.googleapis.com/css?family=Open+Sans:400);\n'\
            '@import url(http://weloveiconfonts.com/api/?family=fontawesome);\n'\
            '* { margin: 0; padding: 0; box-sizing: border-box; }\n'\
            '/* body */\n'\
            'body {background: #e9e9e9;color: #5e5e5e;}\n'\
            '/* Form Layout */\n'\
            '.form-wrapper {background: #fafafa;margin: 3em auto;padding: 2em 1em 2em;max-width: 370px;}\n'\
            'h1 {text-align: center;padding: 1em 0;}\n'\
            'form {padding: 0 1.5em;}\n'\
            '.form-item {margin-bottom: 0.75em;width: 100%;}\n'\
            '.form-item input {background: #fafafa;border: none;border-bottom: 2px solid #e9e9e9;color: #666;font-size: 1em;height: 50px;transition: border-color 0.3s;width: 100%;}\n'\
            '.form-item input:focus {border-bottom: 2px solid #c0c0c0;outline: none;}\n'\
            'button{margin: 2em 0 0;width: 100%;background: #f16272;border: none;color: #fff;cursor: pointer;height: 50px;font-size: 1.2em;letter-spacing: 0.05em;text-align: center;text-transform: uppercase;transition: background 0.3s ease-in-out;width: 100%;}\n'\
            'button:hover {background: #ee3e52;}\n'\
            '.form-footer {font-size: 1em;padding: 2em 0;text-align: center;}\n'\
            '.form-footer .a {color: #8c8c8c;text-decoration: none;transition: border-color 0.3s;}\n'\
            '.form-footer .a:hover {border-bottom: 1px dotted #8c8c8c;}\n'\
            '</style>\n' \
           '</head>\n'\
           '<body>\n' \
           '<div class="form1">\n' \
           '<div class="form-wrapper">\n'\
    # フォームデータを取得
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)
    print(form)

    ########クッキーからID取得、IDをvalに挿入###########
    cookie_str = environ.get('HTTP_COOKIE')
    if cookie_str:
        cookies = cookie_str.split(";")
        for cookie in cookies:
            if 'uID' in cookie:
                a, val = cookie.split("=")      
    ################################################
    
    if('login' in form):
        v1 = form.getvalue("v1", "0")
        v2 = form.getvalue("v2", "0")
        html,response_header = ninsyou(html,v1,v2)
        #login syori
    elif ('regist' in form):
        v1 = form.getvalue("v1", "0")
        v2 = form.getvalue("v2", "0")
        html = regist(html,v1,v2)
    elif ('account' in form):
        html = account(html)
    elif ('hyouka' in form):
        #v1 = form.getvalue("v1", "0")
        html = hyouka(html,val)
    elif ('home' in form):
        html = home(html)
        #IDを一番下に表示
        html += '<br>ようこそ　' + val + '　さん</h1>\n'
    elif('kensaku' in form):
        if('v1' in form):
            v1 = form.getvalue("v1", "0")
            v2 = form.getvalue("v2", "0")
        else :
            v1 = ''
            v2 = ''
        html = kensaku(html,v1,v2,form,val)
        #IDを一番下に表示
        html += '<br>Your ID is ' + val + '</h1>\n'    
    elif('kidoku' in form):
        html = kidoku(html,form,val)
    else:
        html = login(html)

    html += '</html>\n'
    #html = html.encode('utf-8')
    ######↑ 実験の環境ではコメントアウトしてたかも
    # レスポンス
    start_response('200 OK',response_header)
    return [html]

# リファレンスWEBサーバを起動
#  ファイルを直接実行する（python test_wsgi.py）と，
#  リファレンスWEBサーバが起動し，localhost:8080 にアクセスすると
#  このサンプルの動作が確認できる
from wsgiref import simple_server

if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()#! /usr/bin/env python3

