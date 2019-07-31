#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import cgitb
cgitb.enable()
import sys
sys.path.append("/var/www/cgi-bin")
from tweet import Tweet
from datetime import datetime
import re

def application(environ, start_response):
	#HTMLヘッダー
	html = \
		"""
		<html lang="ja">
		<head>
			<meta charset="UTF-8">
			<title>timeline</title>
			<style type="text/css">
				div.div_1{float: left;
				}
				div.div_2{float: left;
				}
			</style>
		</head>
		"""
	#入力フォーム
	inputform = \
			"""
			<body>
                                <div class="div_1">
                                <form>
                                        <p><label>date from(example:2019/6/5):<br><input type="text" name="from"></label></p>
					<p><label>date to:<br><input type="text" name="to"></label></p>
                                        <p><label>username:<br><input type="text" name="username"></label></p>
                                        <p><label>keyword:<br><input type="text" name="keyword"></label></p>
                                        <p><label><input type="submit" value="search"></label></p>
                                        <p><br><br><br></p>
                                        <p><br><input type="button" onclick="location.href = 'userpage'"  value="mypage"></p>
                                </form>
                                </div>

			"""
	#フッター
	foot = \
		"""
                                </div>
                        </body>
                        </html>

                        """
	form = cgi.FieldStorage(environ=environ, keep_blank_values=True)
	#何も入力されていない場合（最初も含む）
	if ("from" not in form) and ("to" not in form) and ("username" not in form) and ("keyword" not in form) :

		html += inputform
		html +=	\
			"""
				<div class="div_2">
				</div>
			</body>
			</html>
			"""
	#入力があった場合
	else:
		html += inputform
		html += ' <div class="div_2">'
		#値を取得
		datefrom = form.getvalue("from")	
		dateto = form.getvalue("to")
		username = form.getvalue("username")
		keyword = form.getvalue("keyword")

		#日付けの入力形式は(2019/6/5)のようにする
		#日付入力が空の場合は,fromはfromtimestamp(0) toはnow()
		#日付入力が形式に合わない場合はエラー
		from_datetime = None
		to_datetime = None
		if not datefrom:
			from_datetime = datetime.fromtimestamp(0)
		elif re.match(r"^\d{4}/\d{1,2}/\d{1,2}$", datefrom):
			from_datetime = datetime.strptime(datefrom, '%Y/%m/%d')
		else:
			html += "Syntax Error: form of date from must be like 2019/6/5"
			html += "<br>"
		if not dateto:
			to_datetime = datetime.now()
		elif re.match(r"^\d{4}/\d{1,2}/\d{1,2}$", dateto):
			to_datetime = datetime.strptime(dateto, '%Y/%m/%d')
		else:
			html += "Syntax Error: form of date to must be like 2019/6/5"
			html += "<br>"

		#日付入力がエラーでない場合
		if from_datetime and to_datetime:
			dates = (from_datetime, to_datetime)

			#Tweet検索
			tweetarray = Tweet.search(keyword, username, dates)

			#tweetを一つづつ表示	
			for tweet in tweetarray:
				html += '<a href="userpage?user={}">{}</a>'.format(tweet.user, tweet.user) + " " + str(tweet.date) + "<br>"
				html += tweet.content + "<br>"
		html += foot

	response_header = [('Content-type', 'text/html')]
	status = '200 OK'
	start_response(status, response_header)
	return [html.encode("utf-8")]

from wsgiref import simple_server
if __name__ == '__main__':
	server = simple_server.make_server('', 8080, application)
	server.serve_forever()
