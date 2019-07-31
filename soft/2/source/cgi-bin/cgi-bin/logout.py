import sys
sys.path.append("/var/www/cgi-bin")
from session import Session

def application(environ, start_response):
    sess = Session(environ['HTTP_COOKIE'])
    sess.logout()
    start_response('200 OK', [('Content-type', 'text/html')])
    return [b'<a href="/login">login</a>']

