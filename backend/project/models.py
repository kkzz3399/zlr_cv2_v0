import mysql.connector
import hashlib  # 用于密码哈希
from config import Config

def get_db_connection():
    """获取数据库连接（增加错误处理）"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            auth_plugin='mysql_native_password'  # 如果认证失败可添加
        )
        return connection
    except mysql.connector.Error as err:
        print(f"数据库连接失败: {err}")
        raise

class User:
    @staticmethod
    def create_user(username, email, password):
        """创建用户（增加邮箱和重复检查）"""
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            # 检查用户名是否已存在
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                raise ValueError("用户名已存在")

            # 检查邮箱是否已存在
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                raise ValueError("邮箱已注册")

            # 密码哈希存储
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # 插入新用户
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            connection.commit()
            return cursor.lastrowid  # 返回新用户的ID
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户"""
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email, password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user

    @staticmethod
    def get_user_by_username(username):
        """根据用户名获取用户（用于登录验证）"""
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user

    @staticmethod
    def get_all_users():
        """获取所有用户"""
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email FROM users")  # 不返回密码
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return users

    @staticmethod
    def update_user(user_id, username=None, email=None, password=None):
        """更新用户信息（可选字段）"""
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            updates = []
            params = []
            if username:
                updates.append("username = %s")
                params.append(username)
            if email:
                updates.append("email = %s")
                params.append(email)
            if password:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                updates.append("password = %s")
                params.append(hashed_password)
            
            if updates:
                query = "UPDATE users SET " + ", ".join(updates) + " WHERE id = %s"
                params.append(user_id)
                cursor.execute(query, tuple(params))
                connection.commit()
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        cursor.close()
        connection.close()
