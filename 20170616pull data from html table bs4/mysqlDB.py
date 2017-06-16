
import pymysql

def connect():
    return pymysql.connect("localhost", "root", "123456", "tradinggroup")

def close_connection(conn):
    conn.close()

def insert(conn, sql):
    with conn.cursor() as cursor:
        cursor.execute(sql)
    conn.commit()
