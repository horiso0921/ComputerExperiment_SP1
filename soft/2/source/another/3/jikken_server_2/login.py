#! /usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
import sqlite3

cgitb.enable()

def loginForm(formDataSet,uId,con):
    html = ''

    form = formDataSet["POST"]

###    if "userName" in form && "password" in form :
###        cur = con.cursor()
###        create_table = 'create table users (username varchar(63),password name varchar(64))'
###        try:
###            cur.execute(create_table)
###        except sqlite3.OperationalError:
###            pass
###      
###       selectPass = 'select password from users where userName = ?'
###        cur.excute(selectPass,form['userName'])
###
###        result = con.fetchall()
###
###        if len(result) < 1:
###            html += '入力されたユーザー名は存在しません<br>\n'
###        elif result[0] == form['password']:
###            html += 'ようこそ ' + form['userName'] + 'さん<br>\n'
###            return html
###        else :
###          html += 'ユーザ名又はパスワードが間違っています<br>\n'

    html += '<div class="form1">\n' \
        '<form action="./" method="POST">\n' \
        'ユーザ名 <input type="text" name="userName"><br>\n' \
        'パスワード <input type="text" name="password"><br>\n' \
        '<button name ="page" value="login">ログイン</button>\n'\
        '<button name ="page" value="register">新規登録</button>\n'\
        '</form>\n' \
        '</div>\n'
 
    return html

def registerForm(formDataSet,uId,con):
    html =''
    form = formDataSet["POST"]

###    if "userName" in form && "password" in form && "passwordRe" in form:
###        userName = form.getvalue("UserName")
###        password = form.getvalue("password")
###        passwordRe = form.getvalue("passwordRe")
###
###        if password == passwordRe:
###     
###            cur = con.cursor()
###            create_table = 'create table users (username varchar(63),password name varchar(64))'
###            try:
###                cur.execute(create_table)
###            except sqlite3.OperationalError:
###                pass
###
###            insertUser = 'insert users (?,?)'
###            cur.excute(insertUser,form['userName'],form['password'])
###
###        else:
###           html += 'パスワードが一致しません\n'
###        elif result[0] == form['password']:
###            html += 'ようこそ ' + form['userName'] + 'さん<br>\n'
###            return html
###        else :
###          html += 'ユーザ名又はパスワードが間違っています<br>\n'
    if uId == -1:
        html += '入力されたユーザー名は既に使われています<br>\n'
    html += '<div class="form1">\n' \
        '<form action="./" method="POST">\n'\
        'ユーザ名 <input type="text" name="userName"><br>\n' \
        'パスワード <input type="text" name="password"><br>\n' \
        'パスワード(確認) <input type="text" name="passwordRe"><br>\n' \
        '<button name ="page" value="register">新規登録</button>\n'\
        '</form>\n' \
        '</div>\n'
  
    return html
