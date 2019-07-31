#! /usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
import sqlite3
import login
import detail
DNAME = 'database.db'
#dbname = ':memory:'

cgitb.enable()

def application(environ,start_response):

    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>WSGI テスト</title>\n' \
           '<link rel="stylesheet" href="default.css">\n' \
           '</head>\n'\
           '<body>\n'
        
    con = sqlite3.connect(DNAME)
    con.text_factory = str

    form = cgi.FieldStorage(fp = environ['wsgi.input'],environ=environ,keep_blank_values=True)
    page = form.getvalue("page","login")
    if page == "login":
        html += login.loginForm(environ,1,con)
    elif page == "register":
        html += login.registerForm(environ,1,con)
    elif page == "detail":
        html += detail.detailPage(environ,1,con)
    elif page == "search":
        html += search.searchPage(environ,1,con)
    html += '</body>\n'\
        '</html>\n'
    response_header = [('Content-type','text/html')]
    status = '200 OK'
    start_response(status,response_header)
    return [html]

from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
