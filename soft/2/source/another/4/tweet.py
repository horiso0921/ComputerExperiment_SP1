#! /usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
import sqlite3

import Cookie

cgitb.enable()

dbname = '/database/tweet.db'
#dbname = ':memory:'

def application(environ, start_response):

    cookie = Cookie.SimpleCookie()

    html = '<html lang = "ja">\n'
    html += '<head>\n'
    html += '<meta charset = "UTF-8">\n'
    html += '<title>さえずり</title>\n'
    html += '<!-- Compiled and minified CSS --> '\
      '<meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">'\
      '<!-- Compiled and minified JavaScript -->'\
      '<script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>' \
      '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.8.2/css/all.css" integrity="sha384-oS3vJWv+0UjzBfQzYUhtDYW+Pj2yciDJxpsK1OYPAYjqT085Qq/1cq5FLXAZQ7Ay" crossorigin="anonymous">'
    html += '</head>\n'

    form = cgi.FieldStorage(environ = environ, keep_blank_values = True)

    html += '<body style = "background: linear-gradient(0deg, #ffd600 0%,#ffea00 50%,#ffff00 100%);">\n'
    html += '<div class="container">\n'
    html += '	<div class = "form1">\n'
    html += '		<form>\n'
    html += '			<div class="row"><div class="col s5"><h1>さえずり</h1></div>'
    html += '<div class="col s7"><a href="/home" class="btn btn-large" style="width:100%;margin-top:50px;"><i class="fas fa-home">ホーム</i></a></div></div>'
    html += '<div class="input-field col s12"><textarea id="textarea1" name="body" class="materialize-textarea"></textarea><label for="textarea1">あなたの今の気持ち</label></div>'
    html += '			<div style = "text-align:center"><button class="waves-effect waves-light btn-large red darken-1 pulse" type = "submit">さえずり！！</button></div>\n'
    html += '		</form>\n'
    html += '	</div>\n'
    html += '</div></body>\n'

    con = sqlite3.connect(dbname)
    con.text_factory = str
    cur = con.cursor()
    create_table = 'create table tweet (body varchar(256), user_id varchar(256), fab_count int, tweet_id int)'

    try:
        cur.execute(create_table)
    except sqlite3.OperationalError:
        pass

    if "body" in form:
        body = form.getvalue("body", "0")
        cookie.load(environ['HTTP_COOKIE'])
        if cookie.has_key("session"):
            user_id = cookie["session"].value
        else:
            html += "ログインしてください。"

            html += '</html>\n'

            reaponse_header = [('Content-type', 'text/html')]
            status = '200 OK'
            start_response(status, reaponse_header)
            return [html]
        num = 0

        sql = 'select count (*) from tweet'
        for row in cur.execute(sql):
            num += int(row[0])

        tweet_id = num + 1

        fab_count = 0

        sql = 'insert into tweet (body, user_id, fab_count, tweet_id) values (?, ?, ?, ?)'
        cur.execute(sql, (body, user_id, fab_count, tweet_id))
        con.commit()



    cur.close()
    con.close()

    html += '</html>\n'

    reaponse_header = [('Content-type', 'text/html')]
    status = '200 OK'
    start_response(status, reaponse_header)
    return [html]

from wsgiref import simple_server

if __name__ == '__main__':
    server = simple_server.make_server('', 8800, application)
    server.serve_forever()
