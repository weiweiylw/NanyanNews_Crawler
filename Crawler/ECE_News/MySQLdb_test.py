# encoding: utf-8

import MySQLdb
import MySQLdb.cursors

# 打开数据库连接
db = MySQLdb.connect("localhost","root","qweasdzxc","nanyan_news" )

# 使用cursor()方法获取操作游标
cursor = db.cursor()

sql = 'INSERT INTO ECE_News(title, date, content) VALUES ("David Young", "2012-1-1 11:11:11", "Shit")'
try:
   # 执行sql语句
   cursor.execute(sql)
   # 提交到数据库执行
   db.commit()
except:
   # Rollback in case there is any error
   db.rollback()
# 关闭数据库连接
db.close()
