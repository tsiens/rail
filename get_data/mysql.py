import pymysql, warnings

warnings.filterwarnings("ignore")


class Mysql():
    def __init__(self, host, user, pwd, basename, tables):
        self.host, self.user, self.pwd, self.basename = host, user, pwd, basename
        self.tables = tables
        nobase = True
        while nobase:
            try:
                self.db = pymysql.connect(self.host, self.user, self.pwd, self.basename, charset="utf8")
                self.db.close()
                nobase = False
                self.create()
            except:
                input('请建立 %s 库' % basename)
                nobase = True

    def create(self):
        create_table = []
        for table, keys in self.tables.items():
            sql = ','.join(['`%s` %s' % (key[0], key[1]) for key in keys])
            sql = "CREATE TABLE IF NOT EXISTS `%s` (%s)" % (table, sql)
            create_table.append(sql)
        self.execute(*create_table)

    def execute(self, *sqls):
        db = pymysql.connect(self.host, self.user, self.pwd, self.basename, charset="utf8")
        cursor = db.cursor()
        back = []
        for sql in sqls:
            try:
                if type(sql) == tuple:
                    cursor.executemany(sql[0], sql[1])
                else:
                    cursor.execute(sql)
                    if 'select' in sql.lower():
                        select = cursor.fetchall()
                        back.append(select)
            except Exception as err:
                log('MYSQL 错误', err, sql)
        db.commit()
        db.close()
        back = back[0] if len(back) == 1 else back
        return back

        # mysql_db = Mysql(mysql_host, mysql_user, mysql_pwd, basename, tables)
