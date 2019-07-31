import csv
import cgi
import cgitb
cgitb.enable()

import sqlite3
dbname = 'proto.db'

#readlist = ['1','2','3','4','5']
def make_database():
    con = sqlite3.connect(dbname)

    cur = con.cursor()
    deldb = 'drop table if exists aozora;'
    cur.execute(deldb)
    makedb = 'create table aozora (id text, title text, class text, release text, updt text, manid text, author text, book text, publish text, enterer text, proof text)'
    cur.execute(makedb)
    cur.execute('CREATE TABLE if not exists readlist(name TEXT, bookid, value INTEGER)')
    con.commit()
    with open('aozora.csv', mode='r') as f:
        b = csv.reader(f)
        #header = next(b)
        for t in b:
            # tableに各行のデータを挿入する。
            cur.execute('INSERT INTO aozora VALUES (?,?,?,?,?,?,?,?,?,?,?);', t)
    con.commit()
    cur.close()
    con.close()

#def make_readlist(environ,n,user):
def make_readlist(environ,n):
    if len(n)!=0:
        dbname = "proto.db"
        con1 = sqlite3.connect(dbname)
        cur1 = con1.cursor()
        con1.text_factory = str
        cur1.execute('CREATE TABLE if not exists readlist(name TEXT, bookid TEXT, value INTEGER)')
        p = "INSERT INTO readlist(name, bookid, value) VALUES(?, ?, ?)"
        form1 = cgi.FieldStorage(environ=environ,keep_blank_values=True)
        for row in n:
            #q2 = (user,str(row),0)
            q2 = (1,str(row),0)
            cur1.execute(p,q2)
            con1.commit()
        con1.commit()
        cur1.close()
        con1.close()

#def re_readlist(environ,n2,user):
def re_readlist(environ,n2):
    dbname = "proto.db"
    con2 = sqlite3.connect(dbname)
    cur2 = con2.cursor()
    con2.text_factory = str
    query = 'select * from readlist'

    form2 = cgi.FieldStorage(environ=environ,keep_blank_values=True)

    con3 = sqlite3.connect(dbname)
    cur3 = con3.cursor()
    for row in cur2.execute(query):
        row2 = form2.getvalue(row[1] ,"0")
        print(row[1],row2)
        #cur3.execute('UPDATE readlist SET value = "'+ str(row2) +'" WHERE bookid = "' +str(row[1])+ '" AND name = "' + user + '"')
        cur3.execute('UPDATE readlist SET value = "'+ str(row2) +'" WHERE bookid = "' +str(row[1])+ '"')
    con3.commit()
    cur3.close()
    con3.close()
    cur2.close()
    con2.close()

def search_id(id):
    temp = "select * from aozora where id like ?"
    #temp += "'%s'"
    return temp
def search_title(title):
    temp = 'select * from aozora where title like ?'
    #temp += '"%'+str(title)+'%"'
    return temp
def search_class(cl):
    temp = 'select * from aozora where class like ?'
    #temp += '"%'+str(cl)+'%"'
    return temp
def search_release(release):
    temp = 'select * from aozora where release like ?'
    #temp += '"%'+str(release)+'%"'
    return temp
def search_update(updt):
    temp = 'select * from aozora where updt like ?'
    #temp += '"%'+str(updt)+'%"'
    return temp
def search_manid(manid):
    temp = 'select * from aozora where manid like ?'
    #temp += '"%'+str(manid)+'%"'
    return temp
def search_book(book):
    temp = 'select * from aozora where book like ?'
    #temp += '"%'+str(book)+'%"'
    return temp
def search_publish(publish):
    temp = 'select * from aozora where publish like ?'
    #temp += '"%'+str(publish)+'%"'
    return temp
def search_enterer(enterer):
    temp = 'select * from aozora where enterer like ?'
    #temp += '"%'+str(enterer)+'%"'
    return temp
def search_proof(proof):
    temp = 'select * from aozora where proof like ?'
    #temp += '"%'+str(proof)+'%"'
    return temp
def search_author(author):
    temp = 'select * from aozora where author like ?'
    #temp += '"%'+str(author)+'%"'
    return temp
def search_readlist(id):
    temp = 'select * from readlist where id=?'
    #temp += '"%'+str(id)+'%"'
    return temp


def application(environ, start_response):
    make_database()
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>Web app</title>\n' \
           '<link rel="stylesheet" href="default.css">\n' \
           '</head>\n'
    
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)
    
    if form.getfirst("update") == "update":
        make_readlist(environ, form.getlist("n"))

    if form.getfirst("update2") == "update":
        re_readlist(environ,form.getlist("n2"))

    if ('v1' not in form):
        html += '<body>\n' \
                '<div class="form1">\n'\
                '<form>\n'\
                'search <input type="text" name="v1"><br>\n'\
                '<select name="v2">\n'\
                '<option value = "id">書籍ID</option>\n'\
                '<option value = "title">タイトル</option>\n'\
                '<option value = "cl">分類番号</option>\n'\
                '<option value = "release">公開日</option>\n'\
                '<option value = "updt">更新日</option>\n'\
                '<option value = "manid">著者ID</option>\n'\
                '<option value = "book">収録本</option>\n'\
                '<option value = "publish">出版社</option>\n'\
                '<option value = "enterer">入力者</option>\n'\
                '<option value = "proof">校正者</option>\n'\
                '<option value = "author">著者</option>\n'\
                '<option value = "read_l">既読リスト</option>\n'\
                '</select>\n'\
                '<input type="submit" value="SEARCH">\n'\
                '</form>'\
                '</div>'\
                '</body>\n'
    
    else:
        v1 = form.getvalue("v1","0")
        v2 = form.getvalue("v2","")
        #temp = search_author(v1)
        #'''
        if v2=="id":
            temp = search_id(v1)
        elif v2=="title":
            temp = search_title(v1)
        elif v2=="cl":
            temp = search_class(v1)
        elif v2=="release":
            temp = search_release(v1)
        elif v2=="updt":
            temp = search_update(v1)
        elif v2=="manid":
            temp = search_manid(v1)
        elif v2=="book":
            temp = search_book(v1)
        elif v2=="publish":
            temp = search_publish(v1)
        elif v2=="enterer":
            temp = search_enterer(v1)
        elif v2=="proof":
            temp = search_proof(v1)
        elif v2=="author":
            temp = search_author(v1)
        elif v2=="read_l":
            temp = search_readlist(id)
        #'''
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        con.text_factory = str

        #temp = "select * from aozora where author like '%夏目%'"
        html += '<body>\n' \
                '<div class="ol1">\n' \
        #既読リストじゃない場合
        if (v2!="read_l"):
            read_id = []
            id_temp = 1
            search_read = 'select bookid from readlist where name='
            search_read += str(id_temp)
            for row in cur.execute(search_read):
                read_id.append(row[0])

            html += '<ol>\n' \
                    '<form>\n'
            for row in cur.execute(temp,('%'+v1+'%',)):
                #html += '<input type="checkbox" name="row[0]" value="checked">'
                html_notread =  '<li>' + '<input type="checkbox" name="'+'n'+'" value="'+str(row[0])+'">'+ str(row[0]) +','+str(row[1])+ '</li>\n'
                html_read = '<li>'+ str(row[0]) +','+str(row[1])+ '</li>\n'
                if str(row[0]) in read_id:
                    html += html_read
                else:
                    html += html_notread

            html += '<input type="submit" name="update" value="update">\n'\
                    '</form>\n'
            
        #既読リストが呼ばれた場合
        else:
            #query = 'select * from readlist where name=user'
            query = 'select * from readlist where name=1'
            #get_bookname = 'select title from aozora where id='
            html += '<form>\n'\
                    '<table>\n'\
                    '<caption>既読リスト</caption>\n'\
                    '<tr>\n'\
                    '<th>題名</th>\n'\
                    '<th>評価</th>\n'\
                    '<th>評価の変更</th>\n'\
                    '</tr>\n'
            con2 = sqlite3.connect(dbname)
            cur2 = con2.cursor()
            for row in cur.execute(query):
                getBookName = "select title from aozora where id=" + str(row[1])
                cur2.execute(getBookName)
                temp = cur2.fetchall()
                book_temp = temp[0]
                html += '<tr>\n'\
                        '<td>' + str(book_temp[0]) + '</td>\n'\
                        '<td>' + str(row[2]) + '</td>\n'\
                        '<td><input type="text" name="'  +str(row[1])+  '" value="' + str(row[2]) + '"></td>\n'\
                        '</tr>\n'

            html += '</table>' \
                    '<input type="submit" name="update2" value="update">\n'\
                    '</form>\n'
            cur2.close()
            con2.close()
        html += '</ol>\n' \
                '</div>\n' \
                '<a href="/">検索ページに戻る</a>\n' \
                '</body>\n'

        cur.close()
        con.close()
    html += '</html>\n'
    html = html.encode('utf-8')

    # レスポンス
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))) ])
    return [html]



from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
