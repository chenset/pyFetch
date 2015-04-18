import MySQLdb


class Mysql:
    conn = None
    cursor = None
    cursor = None
    cursor = None
    cursor = None

    def __init__(self):
        self.conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="spider", charset="utf8")

    @staticmethod
    def get():
        mysql = Mysql.get_instance()
        return mysql.conn

    @staticmethod	
    def get_instance():
        if Mysql.instance is None:
            Mysql.instance = Mysql()

        return Mysql.instance