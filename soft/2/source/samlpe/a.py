import cgi
from wsgiref.simple_server import make_server
 
 
# HTML文字列
html = '''
<!DOCTYPE html>
<html>
  <head>
    <title>WSGI</title>
    <meta charset="UTF-8">
  </head>
  <body>
    {}
    <hr>
    {}
    <hr>
    {}
  </body>
</html>
'''
 
def parse_query(params):
    name = '未入力'
    email = '未入力'
 
    for param, value in params:
        if param == 'name':
            name = value
        elif param == 'email':
            email = value
 
    errors = []
    if name == '未入力':
        errors.append('メールアドレスの入力がありません。')
    if email == '未入力':
        errors.append('お名前の入力がありません。')
 
    return name, email, errors
 
 
def test_app(environ, start_response):
 
    start_response('200 OK', [('Content-Type','text/html')])
 
    # フォームから値を取得（ GET ）
    query = cgi.parse_qsl(environ.get('QUERY_STRING'))
    name, email, errors = parse_query(query)
 
    result = 'お名前：{}<br />'.format(name)
    result += 'メールアドレス: {}'.format(email)
 
    # 結果を表示
    return [html.format(
        'リクエストは {} です。'.format(environ.get('REQUEST_METHOD')),
        result, 
        '<br />'.join(errors)
    ).encode('UTF-8')]
 
 
# WSGIテストサーバーの作成
with make_server('', 8000, test_app) as httpd:
 
    # テストサーバーによる待ち受け
    print('Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...')
    httpd.serve_forever()