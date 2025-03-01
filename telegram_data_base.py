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
            sql = "SELECT * FROM users WHERE promotion_code = %s"
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
    


def get_balance(user_id):
    try:
        with connection.cursor() as cursor:
            # Query to fetch the balance from the users table
            cursor.execute("SELECT wallet FROM users WHERE promotion_code = %s", (user_id,))
            
            # Fetch the first result
            result = cursor.fetchone()
            print("Query executed. Result:", result)  # Debugging print

    except Exception as e:
        print(f"Error getting user balance: {e}")

    return result

get_balance(6001068123)


def get_user_pass(user_id):

    try:
        with connection.cursor() as cursor:

            cursor.execute("SELECT username, password FROM users WHERE promotion_code = %s", (user_id,))
            result = cursor.fetchone()

    except Exception as e:
        print(f"Error getting user balance: {e}")

    return result


def update_wallet(user_id, amount):

    try:

        with connection.cursor() as cursor:

            cursor.execute("UPDATE users SET wallet = wallet + %s WHERE promotion_code = %s", (amount, user_id))
            connection.commit()

        print(f"Added {amount} to user {user_id}'s wallet successfully.")

    except Exception as e:
        print(f"Error updating balance: {e}")

    return amount

user_id = 12345
amount = 200000



def update_wallet_with_commossion(user_id_1, user_id_2, amount):

    try:

        with connection.cursor() as cursor:

            raw_amount = (amount * (90/100))
            cost_amount = (amount * (10/100))

            print(raw_amount, cost_amount)

            cursor.execute("UPDATE users SET wallet = wallet + %s WHERE promotion_code = %s", (raw_amount, user_id_1))
            connection.commit()

            cursor.execute("UPDATE users SET wallet = wallet + %s WHERE promotion_code = %s", (cost_amount, user_id_2))
            connection.commit()

        print(f"Added {raw_amount} to user {user_id}'s wallet successfully. and added {cost_amount} to user {user_id_2}")

    except Exception as e:
        print(f"Error updating balance: {e}")

user_id_1 = 6001068123
user_id_2 = 12345
amount = 100000


def update_wallet(first_user, amount):

    try:
        with connection.cursor() as cursor:

            cursor.execute("UPDATE users SET wallet = wallet + %s WHERE promotion_code = %s", (amount, first_user))
            connection.commit()

            print(f'first user updated amount is {amount}')

    except Exception as e:
        print(f"Error getting user balance: {e}")

    return result

first_user = 7253370126
second_user = 6001068123


def update_wallet_cost(first_user, amount):

    try:
        with connection.cursor() as cursor:

            cursor.execute("UPDATE users SET wallet = wallet - %s WHERE promotion_code = %s", (amount, first_user))
            connection.commit()

            print(f'first user updated amount is {amount}')

    except Exception as e:
        print(f"Error getting user balance: {e}")

    return result



def save_service(name, type, profile, price):

    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO services (name, type, profile, price)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                type = VALUES(type),
                profile = VALUES(profile),
                price = VALUES(price)
            """
            cursor.execute(sql, (name, type, profile, price))
        connection.commit()
    finally:
        connection.close()


# price=20000
# save_service('service2', 'v2ray', '1month', price)


def services():
    all_services = []
    
    # Database connection
    connection = pymysql.connect(**db_config)
    
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM services'
            cursor.execute(sql)
            fetch = cursor.fetchall()  # Fetch all results as dictionaries

        # Directly append dictionaries to the list
        for service in fetch:
            all_services.append({
                'name': service['name'],
                'price': service['price'],
                'profile': service['profile']
            })
  
    except Exception as e:
        print(f'Error retrieving data from database: {e}')
    
    finally:
        connection.close()  # Ensure connection is closed

    return all_services

# Example usage
# services()

# service_name = []

# for i in services():
#    service_name.append(i['name'])


# for i in service_name:
#     selected_service = service_name[1]


# print(i)

# if i == 'service2':
#     inbound_id = 31

# print(inbound_id)

