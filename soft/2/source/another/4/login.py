

#! /usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
cgitb.enable()

import sqlite3

import Cookie
import os

userdb = '/database/user.db'
#userdb = ':memory:'

fabdb = '/database/fab.db'
#fabdb = ':memory:'

tweetdb = '/database/tweet.db'
#tweetdb = ':memory:'

def application(environ,start_response):

    cookie = Cookie.SimpleCookie()
    con = sqlite3.connect(userdb)
    cur = con.cursor()
    create_table = 'create table users (user_id varchar(256), password varchar(256))'
    try:
        cur.execute(create_table)
    except sqlite3.OperationalError:
        pass
    con.commit()
    cur.close()
    con.close()

    con = sqlite3.connect(fabdb)
    cur = con.cursor()
    create_table = 'create table fab (user_id varchar(256), tweet_id int)'
    try:
        cur.execute(create_table)
    except sqlite3.OperationalError:
        pass
    con.commit()
    cur.close()
    con.close()

    con = sqlite3.connect(tweetdb)
    cur = con.cursor()
    create_table = 'create table tweet (body varchar(256), user_id varchar(256), fab_count int, tweet_id int)'
    try:
        cur.execute(create_table)
    except sqlite3.OperationalError:
        pass
    con.commit()
    cur.close()
    con.close()

    con = sqlite3.connect(userdb)
    cur = con.cursor()
    # HTML
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta name="viewport" content="width=device-width,initial-scale=1"><meta charset="UTF-8">\n' \
           '<title></title>\n' \
           '<link rel="stylesheet" href="default.css">\n' \
           '<style type="text/css">' \
           '.ID {display:inline-block;width:80px;text-align:center;}' \
           '.body {display:inline-block;text-align:center;background-color:white;padding:30px;border: solid 2px black;border-radius:30px;box-shadow:20px 30px 333px white;margin-top:50px;font-family: "Kosugi Maru", sans-serif;}' \
           '.main{text-align:center}' \
           '.back{height:100%;background-color:#928c36;background:linear-gradient(#928c36, black)}' \
           '.login_button{margin-top:10px;}' \
           '.img{position:absolute;bottom:0px; right:0px;width:50%;z-index:-1;}' \
           '.welcome {margin-left:30px;margin-top:30px;}' \
           '</style>' \
           '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"><script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script><link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.8.2/css/all.css" integrity="sha384-oS3vJWv+0UjzBfQzYUhtDYW+Pj2yciDJxpsK1OYPAYjqT085Qq/1cq5FLXAZQ7Ay" crossorigin="anonymous">' \
           '</head>\n'

    wsgi_input = environ["wsgi.input"]
    form = cgi.FieldStorage(fp = wsgi_input, environ=environ,keep_blank_values=True)

    if (form.getfirst('signUp')):

        html += '<body>\n' \
            '<div class="form1">\n' \
            '<form method = "POST">\n' \
            '<h1>New User</h1>\n'\
            'UserID (Number and Alphabet)<input type="text" name="newId"><br>\n' \
            'Password (Number and Alphabet)<input type="password" name="newPass"><br>\n' \
            '<input type="submit" value="Sign up">\n' \
            '</form>\n' \

    else:
        if ('ID' not in form) or ('password' not in form):



            html += '<body class = "back">\n' \
                '<div class="form1">\n' \
                '<form method = "POST">\n' \
                '<div class = "main">'\
                '<span class = "body">' \
                '<span class = "ID">ID</span><input type="text" name="ID"><br>\n' \
                '<span class = "ID">Password</span><input type="password" name="password"><br>\n' \
                '<input type="submit" name="login" value="login">\n' \
                '<input type="submit" name="signUp" value="new user">\n' \
                '</span>' \
                '</div>' \
                '</form>\n' \



    if ('newId' in form) and ('newPass' in form):
        newId = form.getvalue("newId", "0")
        newPass = form.getvalue("newPass", "0")
        sqlId = 'select * from users WHERE user_id = ?'
        curId = con.execute(sqlId, (newId, ))
        isExistId = False
        for row in curId:
            isExistId = row[0]
        if isExistId != False:
            html += '<H1> Error </H1>\n'
            html += 'that id is not\n'
            html += '<form>\n'
            html += '<input type = "hidden" name = "signUp" value = newuser>\n'
            html += '</form>\n'

        else:
            sql = 'insert into users (user_id, password) values (?,?)'
            cur.execute(sql, (newId,newPass))
            con.commit()
    if (form.getfirst('login')):
        ID = form.getvalue("ID", "0")
        password = form.getvalue("password", "0")
        sqlId = 'select password from users WHERE user_id = ?'
        Pass = "0"
        for row in cur.execute(sqlId, (ID, )):
            print("{0}".format(row[0]))
            Pass = row[0]
        if password == Pass:
            cur.close()
            con.close()
            cookie["session"] = str(ID)
            url = "/mypage"
            response_header = [('Location', url), ('Set-Cookie', cookie["session"].OutputString())]
            status = '301 Moved'
            start_response(status, response_header)
            return ''
        else:
            html += "Login Error<br>\n"
            html += "input current login password and id<br>\n"
        cur.close()
        con.close()
    html += '</div>\n'
    html += '</body>\n'
    html += '</html>\n'

    response_header = [('Content-type','text/html')]
    status = '200 OK'
    start_response(status,response_header)
    return [html]

from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
