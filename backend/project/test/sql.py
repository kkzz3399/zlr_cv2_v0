import mysql.connector
from mysql.connector import Error

try:
    # 请修改以下连接参数
    connection = mysql.connector.connect(
        host='localhost',  # 数据库主机地址
        port='3306',       # 端口号，默认3306
        database='work',  # 数据库名称
        user='root',           # 用户名
        password='1234'        # 密码
    )
    
    if connection.is_connected():
        db_info = connection.get_server_info()
        print("成功连接到MySQL服务器，版本:", db_info)
        
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print("当前连接的数据库:", record[0])

except Error as e:
    print("连接MySQL数据库时出错:", e)
    
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL连接已关闭")