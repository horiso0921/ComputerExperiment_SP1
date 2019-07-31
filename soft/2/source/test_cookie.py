#! /usr/bin/python
# -*- coding: utf-8 -*-

def application1(environ,start_response):
    # HTML
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<link rel="icon" href="favicon.ico">' \
           '<title>Application 1</title>\n' \
           '</head>\n' \
           "<body><h1>I'm application1.<br />\n"
    # レスポンス
    status = '200 OK'
    response_header = [('Content-type','text/html'),
            ('Set-Cookie','login=0')]
    # login クッキーの処理
    cookie_str = environ.get('HTTP_COOKIE')
    if cookie_str:
        cookies = cookie_str.split(";")
        for cookie in cookies:
            if 'login' in cookie:
                _, val = cookie.split("=")
                val = str( int(val)+1 )
                response_header = [('Content-type','text/html'),
                        ('Set-Cookie','login='+val)]
                html += 'You visited here ' + val + ' times.</h1>\n'
    html += '</body></html>'
    return status, response_header, html

def application2(environ,start_response):
    # HTML
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<link rel="icon" href="favicon.ico">' \
           '<title>Application 2</title>\n' \
           '</head>\n' \
           "<body><h1>I'm application2.<br />\n"
    # レスポンス
    status = '200 OK'
    response_header = [('Content-type','text/html'),
            ('Set-Cookie','login=1')]
    # login クッキーの処理
    cookie_str = environ.get('HTTP_COOKIE')
    if cookie_str:
        cookies = cookie_str.split(";")
        for cookie in cookies:
            if 'login' in cookie:
                a, val = cookie.split("=")
                val = str( int(val)+1 )
                response_header = [('Content-type','text/html'),
                        ('Set-Cookie','login='+val)]
                html += 'You visited here ' + val + ' times.</h1>\n'
    html += '</body></html>'
    return status, response_header, html

def application(environ,start_response):
    flg_login = False
    # login クッキーの処理
    cookie_str = environ.get('HTTP_COOKIE')
    if cookie_str:
        cookies = cookie_str.split(";")
        print(cookies)
        for cookie in cookies:
            if 'login' in cookie:
                flg_login = True
                _, val = cookie.split("=")
                print(val)
                if int(val) % 2 == 0:
                    print(1)
                    status, response_header, html = application1(environ,start_response)
                else:
                    status, response_header, html = application2(environ,start_response)
        if not flg_login:
            status, response_header, html = application1(environ,start_response)
    else:
        status, response_header, html = application1(environ,start_response)

    start_response(status, response_header)
    print(response_header)
    return [html.encode("utf-8")]

# リファレンスWEBサーバを起動
from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
