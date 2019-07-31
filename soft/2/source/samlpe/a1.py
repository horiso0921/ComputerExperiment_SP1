import cgi
from wsgiref.simple_server import make_server
 
 
# 入力HTML文字列
input_html = '''
<!DOCTYPE html>
<html>
  <head>
    <title>CGI</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <form method="POST" action="/">
      <input type="text" name="name">
      <input type="text" name="email">
      <input type="submit">
    </form>
  </body>
</html>
'''
 
# 結果HTML文字列
result_html = '''
<!DOCTYPE html>
<html>
  <head>
    <title>CGI</title>
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
 
def parse_query(query):
    name = '未入力'
    email = '未入力'
 
    for param, value in query:
        if param == b'name':
            name = value.decode('UTF-8')
        elif param == b'email':
            email = value.decode('UTF-8')
 
    errors = []
    if name == '未入力':
        errors.append('メールアドレスの入力がありません。')
    if email == '未入力':
        errors.append('お名前の入力がありません。')
 
    return name, email, errors
 
def test_app(environ, start_response):
 
    start_response('200 OK', [('Content-Type','text/html')])
    method = environ.get('REQUEST_METHOD')
 
    # フォームから値を取得
    if method == 'POST':
        wsgi_input = environ['wsgi.input']
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        query = cgi.parse_qsl(wsgi_input.read(content_length).decode('UTF-8'))
        name, email, errors = parse_query(query)
 
        result = 'お名前：{}<br />'.format(name)
        result += 'メールアドレス: {}'.format(email)
 
        # 結果xを表示
        return [result_html.format(
            'リクエストは {} です。'.format(method),
            result, 
            '<br />'.join(errors)
        ).encode('UTF-8')]
 
    return [input_html.encode('UTF-8')]
 
# WSGIテストサーバーの作成
with make_server('', 8080, test_app) as httpd:
 
    # テストサーバーによる待ち受け
    print('Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...')
    httpd.serve_forever()