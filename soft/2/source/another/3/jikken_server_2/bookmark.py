#-*-coding: utf-8 -*-
import cgi
import sqlite3


def bookmarkpage(formDataSet,user_id,con):
	form = formDataSet["GET"]
	cur = con.cursor()
	try:	
		
		cur.execute('create table bookmarks (name varchar(64),bookId int)')
	except:
		pass
	
	html = '<form method="GET" onsubmit="./"><input type="hidden" name="page" value="edit">'	
	html +='<table style = "border: 1px black solid">'\
		'<thead>'\
		'<tr>'\
			'<th>チェック</th>'\
			'<th>書籍名</th>'\
			'<th>著者</th>'\
			'<th></th>'\
		'</tr>'\
		'</thead>'\
		'<tbody>'	
	sel_id = 'select bookId from bookmarks where name=?'
	cur.execute(sel_id,(user_id,))
	result = cur.fetchall()
	for i in result:
		sel_title_writer = 'select title,author,bookId from books where bookId=?'
		cur.execute(sel_title_writer,(i[0],))
		data = cur.fetchall()[0]
		html +='<tr>'\
			'<td><input type="checkbox" name="check" value='+str(data[2])+'></td>'\
			'<td><li>'+data[0]+'</li></td>'\
			'<td><li>'+data[1]+'</li></td>'\
			'<td><a href = "/?page=detail&bookId='+str(data[2])+'">詳細</a></td>'\
			'</tr>\n'
	html += '</tbody></table>'
	
	html += '<input type ="submit" name = "del" value = "削除">'\
		'</form>'
	
	if "check" in form:
		check = form["check"].split(",")
		for delid in check:
			sql = 'delete from bookmarks where name="'+user_id+'" and bookId="'+delid+'"'
			cur.execute(sql)
		return html
