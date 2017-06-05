# _*_ coding:utf-8 _*_
import MySQLdb

##------------创建表-----------##
class Sql():
    def __init__(self):
        self.db = MySQLdb.connect(host="localhost",
                     port=3306,
                     user="root",
                     passwd="123321",
                     db="book",
                     charset="utf8"
                     )
        self.cur = self.db.cursor() # 使用cursor()方法获取操作游标

##---------创建id,tieba,name,email,telephone,thread,tid,cid字段------##
    def mysql_create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS `tieba` (
          `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
          `tieba` varchar(255) DEFAULT NULL,
          `name` varchar(255) DEFAULT NULL,
          `email` varchar(255) DEFAULT NULL,
          `telephone` varchar(255) DEFAULT NULL,
          `thread` varchar(255) DEFAULT NULL,
          `tid` bigint(20) unsigned NOT NULL,
          `cid` bigint(20) NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;
        """
        self.cur.execute(sql)
        return

##----------------插入数据表中------------------##
    def mysql_insert_data(self,x):
        sql = "INSERT INTO `tieba` (`id`,`tieba`,`name`,`thread`,`email`,`telephone`,`tid`,`cid`) VALUES (0,%s,%s,%s,%s,%s,%s,%s)"
        param = (x['tieba'], x['name'], x['thread'], ','.join(x['email']), ','.join(x['telephone']), x['tid'], x['cid'])
        try:
            # 执行SQL语句
            self.cur.execute(sql,param)
            # 向数据库提交
            self.db.commit()
            print '插入成功'
        except Exception, e:
            # 发生错误时回滚
            # db.rollback()
            print e.message

if __name__ == '__main__':
    a = Sql()
    kenny = a.mysql_create_table()
    chris = a.mysql_insert_data()
