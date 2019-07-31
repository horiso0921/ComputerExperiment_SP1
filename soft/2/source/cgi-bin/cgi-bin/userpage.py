import os
import cgi
import cgitb
from collections import defaultdict
from wsgiref import simple_server
from string import Template
from datetime import datetime

import sys
sys.path.append("/var/www/cgi-bin")
from session import Session
from user import User
from tweet import Tweet

cgitb.enable()

here = os.path.dirname(__file__)

# tweetクラス -> tweet_block.html　に変換する関数
with open(os.path.join(here, "tweet_block.html"), "r", encoding="utf-8") as tb:
    tweet_block_template = Template(tb.read())


def make_tweet_block(tw):
    tweet_variables = defaultdict(str, {
        'tweeter': tw.user,
        'date': tw.date,
        'tweet_content': tw.content,
    })
    return tweet_block_template.substitute(tweet_variables)


def mypage(environ, start_response):
    # Userインスタンスをログイントークンから取得
    token_cookie = environ['HTTP_COOKIE']
    user = Session(token_cookie).user
    # ツイートのリスト
    tweets = Tweet.search(user=user.name, date=(
        datetime.fromtimestamp(0), datetime.now()))

    # クラスから必要な情報を取り出す
    user_variables = defaultdict(str, {
        'username': user.name,
        'followee': len(user.following()),
        'follower': len(user.followers()),
        'tweet_blocks': "\n".join(list(map(make_tweet_block, tweets)))
    })

    # テンプレートに埋め込む
    with open(os.path.join(here, "mypage.html"), "r", encoding="utf-8") as mp:
        html_template = Template(mp.read())

    html = html_template.substitute(user_variables)

    start_response('200 OK', [('Content-type', 'text/html')])
    return [html.encode('utf-8')]


def others_page(environ, start_response, page_user):
    # ツイートのリスト
    tweets = Tweet.search(user=page_user.name)

    # ログインしているユーザのインスタンス
    token_cookie = environ['HTTP_COOKIE']
    logging_user = Session(token_cookie).user

    is_following = any(map(lambda followee: followee.name ==
                           page_user.name, logging_user.following()))

    # クラスから必要な情報を取り出す
    user_variables = defaultdict(str, {
        'username': page_user.name,
        'followee': len(page_user.following()),
        'follower': len(page_user.followers()),
        'follow_button': 'フォローを外す' if is_following else 'フォローする',
        'tweet_blocks': "\n".join(list(map(make_tweet_block, tweets)))
    })

    # テンプレートに埋め込む
    with open(os.path.join(here, "others_page.html"), "r", encoding="utf-8") as mp:
        html_template = Template(mp.read())

    html = html_template.substitute(user_variables)

    start_response('200 OK', [('Content-type', 'text/html')])
    return [html.encode('utf-8')]


def application(environ, start_response):
    # GETやPOSTのクエリの辞書
    request = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

    # ログインしているユーザ
    session = Session(environ['HTTP_COOKIE'])
    logging_user = session.user

    # ログイン中でないならログインしてもらう
    if logging_user.name is None:
        start_response('301 Moved', [('Location', '/login')])
        return ''

    # 指定されたページのユーザ
    page_user = User(request.getvalue('user', logging_user.name))

    if environ['REQUEST_METHOD'] == 'POST':
        # 内容が送信されてきたらそれをツイートする
        tweet_content = request.getvalue('tweet_content')
        if tweet_content:
            logging_user.tweet(tweet_content)
            # 二重投稿を防ぐリダイレクト
            start_response('301 Moved', [('Location', '/userpage')])
            return ''

        # フォロー、フォロー解除があれば反映する
        toggle_following = request.getvalue('toggle_following')
        if toggle_following == 'フォローする':
            logging_user.follow(page_user)
        if toggle_following == 'フォローを外す':
            logging_user.unfollow(page_user)
            # 二重投稿を防ぐリダイレクト
            start_response(
                '301 Moved', [('Location', '/userpage?user={}'.format(page_user.name))])
            return ''

    # クエリによって振り分ける
    if logging_user.name == page_user.name:
        return mypage(environ, start_response)
    else:
        return others_page(environ, start_response, page_user)


if __name__ == "__main__":
    server = simple_server.make_server('', 8080, userpage)
    server.serve_forever()
