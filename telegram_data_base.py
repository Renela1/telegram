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

def save_user(user_id, username, promotion_code, wallet, seller_code):
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
                INSERT INTO users (id, username, promotion_code, wallet, seller_code)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                username = VALUES(username),
                promotion_code = VALUES(promotion_code),
                wallet = VALUES(wallet),
                seller_code = VALUES(promotion_code),
            """
            cursor.execute(sql, (user_id, username, Update.message.from_user.id, 0, seller_code))
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

def sign_up(username, password, promotion_code, wallet, seller):
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
            sql = "INSERT INTO users (username, password, promotion_code, wallet, seller_code) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (username, password, promotion_code, wallet, seller))
            
            if seller != promotion_code:
                connection.commit()
                return True  # User registered successfully
            else:
                return False
        
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

            raw_amount = (amount * (80/100))
            cost_amount = (amount * (20/100))

            print(raw_amount, cost_amount)

            cursor.execute("UPDATE users SET wallet = wallet - %s WHERE promotion_code = %s", (amount, user_id_1))
            connection.commit()

            cursor.execute("UPDATE users SET wallet = wallet + %s WHERE promotion_code = %s", (cost_amount, user_id_2))
            connection.commit()

        print(f"cost {raw_amount} to user {user_id}'s wallet successfully. and added {cost_amount} to user {user_id_2}")

    except Exception as e:
        print(f"Error updating balance: {e}")

user_id_1 = 6001068123
user_id_2 = 12345
amount = 80000

def distribute_commission(user_promo_code, service_id, selling_price):
    try:
        with connection.cursor() as cursor:
            # Step 1: Get Base Price from 'services' Table
            cursor.execute("SELECT price FROM services WHERE id = %s", (service_id,))
            service_data = cursor.fetchone()
            if not service_data:
                print("⚠️ Service not found!")
                return
            
            deduct_query = "UPDATE users set wallet = wallet - %s where promotion_code = %s"
            cursor.execute(deduct_query, (amount, user_promo_code))
            connection.commit()

            base_price = int(service_data['price'] ) # Base price (e.g., 50,000)
            markup = int(selling_price - base_price)  # Extra profit to be split

            if markup <= 0:
                print("⚠️ No extra markup to distribute.")
                return

            # Step 2: Get the Chain of Sellers
            sellers = []
            current_user = user_promo_code  # Start from the buyer's seller
            while current_user:
                cursor.execute("SELECT seller_code FROM users WHERE promotion_code = %s", (current_user,))
                result = cursor.fetchone()
                if not result or not result['seller_code']:
                    break  # Stop if no more sellers

                next_seller = result['seller_code']
                sellers.append(next_seller)  # Add to seller list
                current_user = next_seller

            # Step 3: Distribute the Profit Evenly
            num_sellers = len(sellers)
            if num_sellers == 0:
                print("⚠️ No sellers to distribute commission.")
                return

            share_per_seller = int(markup / num_sellers)  # Equal split

            # Step 4: Update Wallets of Sellers
            for seller_code in sellers:
                cursor.execute("UPDATE users SET wallet = wallet + %s WHERE promotion_code = %s",
                               ((int(share_per_seller)), seller_code))
                connection.commit()
                print(f"✅ {(int(share_per_seller))} added to seller {seller_code}")

            print(f"✅ {markup} successfully distributed among {num_sellers} sellers.")

    except Exception as e:
        print(f"❌ Error in commission distribution: {e}")


# print(distribute_commission(user_id_2,26, amount))


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


def save_service(name, type, profile, price, promotion_code):

    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO services (name, type, profile, price, promotion_code)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                type = VALUES(type),
                profile = VALUES(profile),
                price = VALUES(price),
                promotion_code = VALUES(promotion_code)
            """
            cursor.execute(sql, (name, type, profile, price, promotion_code))
        connection.commit()
    finally:
        connection.close()


# price=20000
# save_service('my_service', 'v2ray', '1month', price, promotion_code=7253370126)


def services(user_id):

    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT seller_code FROM users WHERE promotion_code = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            code = result['seller_code']

    except Exception as e: print(e)

    all_services = []

    connection = pymysql.connect(**db_config)
    
    try:
        with connection.cursor() as cursor:
            sql = f'SELECT * FROM services WHERE promotion_code = {code}'
            cursor.execute(sql)
            fetch = cursor.fetchall()  # Fetch all results as dictionaries

        # Directly append dictionaries to the list
        for service in fetch:
            all_services.append({
                'name': service['name'],
                'price': service['price'],
                'profile': service['profile'],
                'promotion_code': service['promotion_code']
            })
  
    except Exception as e:
        print(f'Error retrieving data from database: {e}')
    
    finally:
        connection.close()  # Ensure connection is closed

    return all_services

# print(services(6001068123))

import pymysql

def retrieve_services(promotion_code):
    services = []
    connection = pymysql.connect(**db_config)  # Ensure db_config is defined

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get user_id from promotion_code
            cursor.execute("SELECT id FROM users WHERE promotion_code = %s;", (promotion_code,))
            user_row = cursor.fetchone()

            if not user_row:
                print(f"⚠️ No user found with promotion_code = {promotion_code}")
                return []  # No user found, return empty list
            
            user_id = user_row['id']

            # Query to retrieve service details
            query = """
            SELECT 
                us.id AS user_service_id, 
                us.service_id AS user_service_service_id,  -- FK in User_Services
                s.id AS actual_service_id,  -- Actual Service ID from Services table
                s.profile, 
                s.type, 
                s.name, 
                COALESCE(us.price, s.price, 0) AS final_price  -- Ensure no NULL prices
            FROM User_Services us
            JOIN services s ON us.service_id = s.id
            WHERE us.user_id = %s;
            """  

            cursor.execute(query, (user_id,))
            fetch = cursor.fetchall()

            if not fetch:
                print(f"⚠️ No services found for user_id = {user_id}")

            services = [
                {
                    'user_service_id': service['user_service_id'],
                    'user_service_service_id': service['user_service_service_id'],
                    'name': service['name'],
                    'price': service['final_price'],
                    'profile': service['profile'],
                    'type': service['type']
                }
                for service in fetch
            ]

    except Exception as e:
        print(f"❌ Database Error: {e}")

    finally:
        connection.close()

    return services


# print(retrieve_services(6001068123))


def buy_services(user_id):
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get seller's promotion_code
            sql = "SELECT seller_code FROM users WHERE promotion_code = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

            if not result:  # Handle case where user doesn't exist
                return {"error": "User not found or has no seller."}

            seller_code = result['seller_code']

            # Retrieve seller's services
            query = """
            SELECT 
                us.id AS user_service_id, 
                us.user_id, 
                us.service_id AS user_service_service_id, 
                u.promotion_code AS telegram_id,
                s.profile,  
                s.type,
                s.name, 
                s.price AS original_price, 
                us.price AS user_price       
            FROM User_Services us
            JOIN users u ON us.user_id = u.id
            JOIN services s ON us.service_id = s.id
            WHERE u.promotion_code = %s;
            """
            
            cursor.execute(query, (seller_code,))
            fetch = cursor.fetchall()

    except Exception as e:
        return {"error": str(e)}

    finally:
        connection.close()  # Ensure connection is always closed

    # Format the response
    services = [{
        'name': service['name'],
        'price': service['user_price'],
        'original_price': service['original_price'],
        'profile': service['profile'],
        'promotion_code': service['telegram_id'],
        'type': service['type'],
        'user_service_id': service['user_service_service_id']
    } for service in fetch]

    return services

# Example usage
# print(buy_services(6001068123))

def update_service_price(user_id, service_id, new_price):
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Step 1: Get the seller_code of the user
            sql = "SELECT seller_code FROM users WHERE promotion_code = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

            if not result:
                return {"error": "User not found or has no seller."}

            seller_code = result["seller_code"]

            # Step 2: Get the minimum price from the seller
            query = """
            SELECT us.price AS min_price 
            FROM User_Services us
            JOIN users u ON us.user_id = u.id
            WHERE u.promotion_code = %s AND us.service_id = %s
            """
            cursor.execute(query, (seller_code, service_id))
            seller_service = cursor.fetchone()
            print(seller_service)

            if not seller_service:
                return {"error": "Seller's service not found."}

            min_price = int(seller_service["min_price"])
            
            print(min_price)
            print(seller_code)
            # Step 3: Check if new price is valid
            if new_price < min_price:

                accepted = False
                return {"error": f"New price {new_price} is lower than the minimum allowed price {min_price}."}
            else: accepted = True

            # Step 4: Update the service price for the user
            update_sql = """
            UPDATE User_Services 
            SET price = %s 
            WHERE user_id = (SELECT id FROM users WHERE promotion_code = %s) 
            AND service_id = %s
            """
            cursor.execute(update_sql, (new_price, user_id, service_id))
            connection.commit()

            print({"success": f"Service price updated to {new_price}."})

            return accepted

    except Exception as e:
        return {"error": str(e)}

    finally:
        connection.close()
  

# # Example Usage
# print(update_service_price(6001068123, 3, 280000))


def all_services():
    all_services = []
    
    # Database connection
    connection = pymysql.connect(**db_config)
    
    try:
        with connection.cursor() as cursor:
            sql = f'SELECT * FROM services'
            cursor.execute(sql)
            fetch = cursor.fetchall()  # Fetch all results as dictionaries

        # Directly append dictionaries to the list
        for service in fetch:
            all_services.append({
                'name': service['name'],
                'price': service['price'],
                'profile': service['profile'],
                'promotion_code': service['promotion_code']
            })
  
    except Exception as e:
        print(f'Error retrieving data from database: {e}')
    
    finally:
        connection.close()  # Ensure connection is closed

    return all_services


def add_seller_services_to_user(user_id):

    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
         
            cursor.execute("SELECT seller_code FROM users WHERE promotion_code = %s", (user_id,))
            result = cursor.fetchone()

            if not result:
                return {"error": "User not found or has no seller."}

            seller_code = result["seller_code"]

            query = """
            SELECT us.service_id, us.price
            FROM User_Services us
            JOIN users u ON us.user_id = u.id
            WHERE u.promotion_code = %s;
            """

            cursor.execute(query, (seller_code,))
            seller_services = cursor.fetchall()

            if not seller_services:
                return {"error": "Seller has no services."}

         
            for service in seller_services:
                service_id = service["service_id"]
                price = service["price"] 

                # Check if the user already has this service
                check_query = """
                SELECT COUNT(*) AS count FROM User_Services 
                WHERE user_id = (SELECT id FROM users WHERE promotion_code = %s) 
                AND service_id = %s;
                """
                cursor.execute(check_query, (user_id, service_id))
                exists = cursor.fetchone()["count"]

                if exists == 0:  # If service is not already assigned, add it
                    insert_query = """
                    INSERT INTO User_Services (user_id, service_id, price)
                    VALUES ((SELECT id FROM users WHERE promotion_code = %s), %s, %s);
                    """
                    cursor.execute(insert_query, (user_id, service_id, price))
                else:
                    return {'failed': 'records already exist for user'}

            connection.commit()
            return {"success": "Seller's services successfully added to the user."}

    except Exception as e:
        return {"error": str(e)}

    finally:
        connection.close()


# print(add_seller_services_to_user(6001068123))