import pymysql
import pymysql.cursors
from telegram import Update

# SQL query to create the table
create_table = """
CREATE TABLE IF NOT EXISTS `users` (
    `username` varchar(255) COLLATE utf8_bin NOT NULL,
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `wallet` float(50),
    `promotion_code` varchar(255) COLLATE utf8_bin NOT NULL,
    `password` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
AUTO_INCREMENT=1 ;
"""

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "PoXRHtR3Wp1g0JuooCKFmLZa",
    "database": "tlbot",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

# Connect to the database
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='PoXRHtR3Wp1g0JuooCKFmLZa',
    database='tlbot',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)


with connection:

    with connection.cursor() as cursor:
        # Check if the record exists
        sql_check = "SELECT id FROM `users` WHERE `username` = %s"
        cursor.execute(sql_check, ('shayan',))
        result = cursor.fetchone()

        if result:
            print("Record with this username already exists.")
        else:
            # Insert the new record if it doesn't exist
            sql_insert = "INSERT INTO `users` (`promotion_code`, `password`, `username`) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert, ('12345', '12345', 'shayan'))
            print("Record inserted successfully!")

    # Commit the changes to the database
    connection.commit()

    with connection.cursor() as cursor:
        # Fetch a single record
        sql = "SELECT `id`, `password`, `promotion_code` FROM `users` WHERE `username`=%s"
        cursor.execute(sql, ('shayan',))
        result = cursor.fetchone()
        print("Fetched record:", result)

def save_user(user_id, username, promotion_code, wallet):
    """
    Saves or updates user information in the database.

    :param user_id: Telegram user ID
    :param username: Telegram username
    :param wallet: 0
    :param promotion_code: Telegram user ID
    """
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO users (id, username, promotion_code, wallet)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                username = VALUES(username),
                promotion_code = VALUES(promotion_code),
                wallet = VALUES(wallet)
            """
            cursor.execute(sql, (user_id, username, Update.message.from_user.id, 0))
        connection.commit()
    finally:
        connection.close()

def get_all_users():
    """
    Retrieves all users from the `users` table.
    """
    try:
        if not connection.open:
            print("Reconnecting to the database...")
            connection.ping(reconnect=True)
        
        with connection.cursor() as cursor:
            sql = "SELECT id, username FROM users"
            print("Executing query:", sql)
            cursor.execute(sql)
            users = cursor.fetchall()
            if not users:
                print("No users found.")
            else:
                print("Users fetched:", users)
            return users
        
    except Exception as e:
        
        print(f"An error occurred: {e}")
        return []
    
get_all_users()

# Function to Get User
def get_user(user_id):
    """
    Fetches user information from the database.

    :param user_id: Telegram user ID
    :return: User record as a dictionary or None if not found
    """
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
        return result
    finally:
        connection.close()


# Function to Log Service Selection
def log_service_selection(user_id, service_name):
    """
    Logs the service selected by a user into the service_logs table.

    :param user_id: Telegram user ID
    :param service_name: Name of the selected service
    """
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO service_logs (user_id, service_name)
                VALUES (%s, %s)
            """
            cursor.execute(sql, (user_id, service_name))
        connection.commit()
    finally:
        connection.close()

def sign_up(username, password, promotion_code, wallet):
    """
    Registers a new user if the username does not exist in the database.
    """
    try:
        with connection.cursor() as cursor:
            # Check if the username already exists
            sql = "SELECT id FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                return False  # Username already exists

            # Insert the new user into the database
            sql = "INSERT INTO users (username, password, promotion_code, wallet) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, password, promotion_code, wallet))

            # Commit the transaction
            connection.commit()
            return True  # User registered successfully
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    

