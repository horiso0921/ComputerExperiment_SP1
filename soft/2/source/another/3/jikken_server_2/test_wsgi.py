#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(__file__))

import login
import booksearch
import bookmark
import book_mypage
import detail
import cgi
import cgitb
import sqlite3
from pprint import pprint
try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs
import random

#dbname = '/mdhome/home8/bb8283818/jikken_server_2/database.db'
dbname = 'database.db'
SESSION_STR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

cgitb.enable()

def getSqliteResult(cur,script):
    print(script)
    r = []
    try:
        cur.execute(script)
        r = cur.fetchall()
    except sqlite3.OperationalError:
        pass
    return r

def issueSessionId(cur,user_name):
    try:
        tmp = getSqliteResult(cur,"select session from sessions where name='"+str(user_name)+"'")
        if(tmp != ""):
            getSqliteResult(cur,"delete from sessions where name='"+str(user_name)+"'")
        session = ""
        while True:
            session+=str(SESSION_STR[random.randrange(0,len(SESSION_STR)-1)])
            if(len(session)>=20):
                if(len(getSqliteResult(cur,"select session from sessions where session='"+session+"'"))==0):
                    break
        getSqliteResult(cur,"insert into sessions values('"+str(user_name)+"','"+session+"')")
        print("issued session "+session+" to "+str(user_name))
        return session
    except sqlite3.OperationalError:
        return ""

def deleteSessionId(cur,session_id):
    getSqliteResult(cur,"delete from sessions where session='"+str(session_id)+"'")

def loadUserBySessionId(cur,session_id):
    print("session_id: "+str(session_id))
    t = getSqliteResult(cur,"select name from sessions where session='"+str(session_id)+"'")
    print("name: "+str(getSqliteResult(cur,"select name from sessions where session='"+str(session_id)+"'")))
    if(len(t)==0):
        return ""
    else:
        return str(t[0][0])

def getTest(environ,user_id,con):
    if user_id==-1:
        return "<form method='post' action='./?page=login'><button>submit!</button></form><br>user load error"
    else:
        return "<form method='post' action='./?page=login'><button>submit!</button></form><br>loaded user_id:"+user_id

def application(environ,start_response):
    
    title = "" #ページのタイトル
    user_name = ""
    session = ""

    status = "" #HTTP status

    response_header = []

    #DB生成
    con = sqlite3.connect(dbname)
    con.text_factory = str
    cur = con.cursor()
    try:
        #usersテーブル
        cur.execute('create table users (name varchar(64), pass varchar(64))')
        print("DB users created")
    except sqlite3.OperationalError:
        pass
    try:
        #sessionsテーブル
        cur.execute('create table sessions (name varchar(64), session varchar(64))')
        print("DB sessions created")
    except sqlite3.OperationalError:
        pass
    try:
        #booksテーブル
        cur.execute('create table books (bookId int, title varchar(64), divN int, relDate varchar(64), lastDate varchar(64), authorId int, author varchar(64), oriBook varchar(64), publisher varchar(64), enterer varchar(64), prreader varchar(64))')
        with open(os.path.dirname(os.path.abspath(__file__))+"/aozora.csv") as csv_raw:
            csv_raw2 = csv_raw.readlines();
            for csv_line in csv_raw2:
                csv_data = csv_line.split(",")
                if(len(csv_data)==11):
                    cur.execute('insert into books values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',(csv_data[0],csv_data[1],csv_data[2],csv_data[3],csv_data[4],csv_data[5],csv_data[6],csv_data[7],csv_data[8],csv_data[9],csv_data[10]))
                else:
                    print("Error: csv row not imported: "+csv_line)
        print("DB books created")
    except sqlite3.OperationalError:
        pass
    
    #param読み込み
    #GETデータの読み込み（Thanks to https://pod.hatenablog.com/entry/2016/04/17/015524 @20190509）
    #POSTデータの読み込み（Thanks to https://ivy-box.net/article/20150918.html @20190425）
    form_g_t = parse_qs(environ["QUERY_STRING"])
    form_g = {} #GET
    for k in form_g_t.keys():
        form_g[k] = form_g_t[k][0]
    form_p = {} #POST
    if 'POST'==environ.get('REQUEST_METHOD'):
        form_p_t = cgi.FieldStorage(fp=environ['wsgi.input'],environ=environ,keep_blank_values=True)
        pprint(form_p_t.keys())
        for k in form_p_t.keys():
            print(k)
            if type(form_p_t[k]) is list:
                form_p[k] = form_p_t[k][0].value
            else:
                form_p[k] = form_p_t[k].value
    form_c = {} #Cookie
    cookie_str = environ.get('HTTP_COOKIE')
    if cookie_str:
        cookies = cookie_str.split(";")
        for cookie in cookies:
            tmp = cookie.split("=")
            form_c[tmp[0].strip()] = tmp[1].strip()
    #POSTでのみpageが入ることがあるのでGET側にコピー
    if "page" not in form_g.keys() and "page" in form_p.keys():
        form_g["page"]=form_p["page"]
    #受け取ったデータを標準出力に出してデバッグ
    print("\nGET:")
    pprint(form_g)
    print("\nPOST:")
    pprint(form_p)
    print("\nCOOKIE:")
    pprint(form_c)
    print("")
    #pageがなければloginに飛ばす
    if 'page' not in form_g:
        form_g['page'] = "login"
    #css
    if form_g['page']=="css":
        response_header.append(('Content-type','text/css'))
        status = '200 OK'
        start_response(status,response_header)
        with open(os.path.dirname(os.path.abspath(__file__))+"/style.css") as css_data:
            return css_data.read();
        return "p{padding: 10px;}"
    #ユーザ処理
    login_status = 0 #0:通常 -1:ユーザ非存在 -2:パスワード違い
    if ('userName' in form_p) and ('password' in form_p) and (form_p['userName']!=""):
        if form_g['page']=="login":
            #ログイン
            try:
                print("users:")
                pprint(getSqliteResult(cur,"select name from users"))
                #usersテーブル
                pw_s = getSqliteResult(cur,"select pass from users where name='"+str(form_p['userName'])+"'")
                if len(pw_s)==0:
                    print("login failed: no such user "+str(form_p['userName']))
                    login_status = -1
                elif str(pw_s[0][0]) == str(form_p['password']):
                    print("login succeed: "+str(form_p['userName']))
                    session = str(issueSessionId(cur,str(form_p['userName'])))
                    response_header.append(('Set-Cookie','session='+session))
                    response_header.append(('Location','./?page=top'))
                    status = "303 See Other"
                elif str(pw_s[0][0])=="":
                    print("login failed: no such user "+str(form_p['userName']))
                    login_status = -1
                else:
                    print("login failed: password wrong, c="+str(pw_s[0][0])+" i="+str(form_p['password']))
                    login_status = -2
            except sqlite3.OperationalError:
                pass
        elif form_g['page']=="register":
            #新規登録
            try:
                #usersテーブル
                user_exist = getSqliteResult(cur,"select * from users where name='"+str(form_p['userName'])+"'")
                if len(user_exist)>0:
                    print("user already exist: "+str(form_p['userName']))
                    user_name = -1
                else:
                    getSqliteResult(cur,"insert into users values('"+form_p["userName"]+"','"+form_p["password"]+"')")
                    print("NEW USER: "+str(form_p['userName']))
                    login_status = 1
                    form_g['page']="login"
            except sqlite3.OperationalError:
                pass
    if form_g['page']=="logout":
        deleteSessionId(cur,form_c["session"])
        response_header.append(('Set-Cookie','session=; Max-Age=0'))
        session=""
        form_g['page']="login"
    elif session=="" and ("session" in form_c.keys()):
        session = str(form_c["session"])
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>'+title+'</title>\n' \
           '<link rel="stylesheet" href="./style.css?page=css">\n' \
           '<style type="text/css">\n' \
           '.header .table{width: 100%;}\n' \
           '.header .table .logout{text-align: right;}\n' \
           '.header a{padding: 5px;}\n' \
           '</style>\n' \
           '</head>\n' \
           '<body>\n' \
           '<div class="header"><table class="table">\n' \
           '<tr>\n' \
           '<td>\n' \
           +title+'\n' \
           '</td>\n' \
           '<td class="logout">\n'
    if session=="":
        html+='ようこそ、ゲストさん！\n'
    else:
        user_name = loadUserBySessionId(cur,session)
        html+='ようこそ、'+user_name+'さん！<a href="./?page=logout">LOGOUT</a>\n'
    html+=  '</td>\n' \
            '</tr>\n' \
            '</table></div>\n' \
            '<hr>\n' \
            '<div>\n'
    #ページ中身
    #
    print("page="+form_g["page"])
    form_data_set = {"GET":form_g, "POST":form_p, "COOKIE":form_c}
    #pprint(form_data_set)
    if form_g["page"]=="login":
        html+= login.loginForm(form_data_set,user_name,con)
    elif form_g["page"]=="register":
        html+= login.registerForm(form_data_set,user_name,con)
    elif form_g["page"]=="search":
        html+= booksearch.booksearch(form_data_set,user_name,con)
    elif form_g["page"]=="edit":
        html+= bookmark.bookmarkpage(form_data_set,user_name,con)
    elif form_g["page"]=="top":
        html+= book_mypage.mypage(form_data_set,user_name,con)
    elif form_g["page"]=="detail":
        html+= detail.detailPage(form_data_set,user_name,con)
    else:
        html+= getTest(environ,user_name,con)
    html = html.strip()
    html+="\n"
    html+= '</div>\n' \
           '</body>\n' \
           '<script type="text/javascript">console.log("'+str(getSqliteResult(cur,"desc users"))+'");</script>' \
           '</html>'
    """
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)
    if ('v1' not in form) or ('v2' not in form):
        html += '<body>\n' \
                '<div class="form1">\n' \
                '<form>\n' \
                '学生番号（整数） <input type="text" name="v1"><br>\n' \
                '氏名　（文字列） <input type="text" name="v2"><br>\n' \
                '<input type="submit" value="登録">\n' \
                '</form>\n' \
                '</div>\n' \
                '</body>\n'
    else:
        con = sqlite3.connect(dbname)
        con.text_factory = str
        cur = con.cursor()
        create_table = 'create table users (id int, name varchar(64))'
        try:
            cur.execute(create_table)
        except sqlite3.OperationalError:
            pass
        v1 = form.getvalue("v1", "0")
        v2 = form.getvalue("v2", "0")
        sql = 'insert into users (id, name) values (?,?)'
        cur.execute(sql, (int(v1),v2))
        con.commit()
        html += '<body>\n' \
                '<div class="ol1">\n' \
                '<ol>\n'
        sql = 'select * from users'
        for row in cur.execute(sql):
            html += '<li>' + str(row[0]) + ',' + row[1] + '</li>\n'
        html += '</ol>\n' \
                '</div>\n' \
                '<a href="/">登録ページに戻る</a>\n' \
                '</body>\n'
        con.close()
    html += '</html>\n'
    """
    response_header.append(('Content-type','text/html'))

    print("COMMIT")
    con.commit()
    con.close()
    if status=="":
        status = '200 OK'
    start_response(status,response_header)
    return [html]

from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
