import requests
import random
import uuid
import json
import telegram_data_base

# Function to add inbound with dynamic parameters
def add_inbound(expiryTime, remark, profile, limit):

    # Generate a random UUID
    client_uuid = uuid.uuid4()
    uuid4 = str(client_uuid)

    # Generate and print a random UUID for the client
    print("Generated Client UUID:",uuid4)
    # The login URL and credentials
    login_url = "https://s1.arganas.com:2053/login"
    credentials = {
        "username": "shadow",  # Replace with actual username
        "password": "sh1sh2sh3"   # Replace with actual password
    }

    # The URL for adding inbound and listing inbounds
    inbound_url = "https://s1.arganas.com:2053/panel/api/inbounds/add"
    list_inbounds_url = "https://s1.arganas.com:2053/panel/api/inbounds/list"

    # Start a session to automatically handle cookies
    session = requests.Session()

    # Login to the server
    try:
        response = session.post(login_url, data=credentials)
        if response.status_code == 200:
            print("Login successful!")
        else:
            print(f"Login failed. Status Code: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print("An error occurred during login:", e)
        return

    # Check the current list of inbounds and gather existing ports
    try:
        inbounds_response = session.get(list_inbounds_url)
        if inbounds_response.status_code == 200:
            print("Raw response from inbounds list:")
            print(inbounds_response.text)  # Print the raw response content
            # Now, we need to inspect the response structure
            existing_ports = []  # Initialize empty list for existing ports
            
            # Try to parse the response as JSON
            try:
                json_data = inbounds_response.json()
                if isinstance(json_data, list):
                    existing_ports = [inbound['port'] for inbound in json_data]
                else:
                    print("Response format is not as expected. It might not be a list.")
                    print("Response data:", json_data)
            except ValueError as e:
                print("Error parsing response as JSON:", e)
                
            print(f"Existing ports: {existing_ports}")
        else:
            print(f"Failed to retrieve inbounds. Status Code: {inbounds_response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print("An error occurred while fetching inbounds:", e)
        return

    # Generate a random port and ensure it doesn't conflict with existing ones
    while True:
        port = random.randint(1024, 65535)
        if port not in existing_ports:
            break
        else:
            print(f"Port {port} is already in use, generating a new one...")

    # Define the payload with dynamic values
    settings = {
    "clients": [{
        "id": uuid4,
        "alterId": 0,
        "email": f"{remark}@gmail.com",
        "limitIp": 2,
        "totalGB": 42949672960,
        "expiryTime": limit,  # Example expiry time in milliseconds
        "enable": True,
        "tgId": "",
        "subId": ""
    }],
    "decryption": "none",
    "fallbacks": []

    }

    payload = {
        "enable": True,
        "remark": remark,  # Dynamic remark
        "listen": "",  # Empty listen value
        "port": port,  # Randomly generated port
        "protocol": "vless",
        "transmission": "TCP(RAW)",
        "expiryTime": expiryTime,  # Dynamic expiryTime
        "settings": json.dumps(settings),
        "streamSettings": "{\"network\":\"tcp\",\"security\":\"none\",\"wsSettings\":{\"acceptProxyProtocol\":false,\"path\":\"/\",\"headers\":{}}}",
        "sniffing": "{\"enabled\":true,\"destOverride\":[\"http\",\"tls\"]}"
    }

    # Send the POST request with the JSON payload to add inbound
    try:
        inbound_response = session.post(inbound_url, json=payload)

        # Check if the request was successful
        if inbound_response.status_code == 200:
            print(f"Successfully added inbound on port {port}!")
            print("Response:", inbound_response.json())  # Print the response if needed
            inbound_data = inbound_response.json()

         
        else:
            print(f"Failed to add inbound. Status Code: {inbound_response.status_code}")
    except requests.exceptions.RequestException as e:
        print("An error occurred while adding inbound:", e)


    # The URL for adding client to the inbound
    
    # Define protocol and security settings (tcp and none based on your format)
    protocol = "tcp"
    security = "none"
    path = "/"  # You can change this if you have a different WebSocket path
    
    # Construct the config URL
    config_url = f"vless://{uuid4}@s1.arganas.com:{port}?encryption=none&security={security}&path={path}#{remark}{port}@gmail.com"
    print(config_url)

    telegram_data_base.save_service(remark, 'v2ray', profile, 30000)

    return config_url


from datetime import datetime, timedelta

# Get current time
now = datetime.utcnow()

# Add 3 months (approx. 90 days)
expiry_time_3 = now + timedelta(days=90)

# Convert to timestamp (milliseconds)
expiry_timestamp_3 = int(expiry_time_3.timestamp() * 1000)

print(expiry_timestamp_3)  # Use this value in your payload

expiry_time_2 = now + timedelta(days=60)

# Convert to timestamp (milliseconds)
expiry_timestamp_2 = int(expiry_time_2.timestamp() * 1000)

print(expiry_timestamp_2)  # Use this value in your payload

expiry_time_1 = now + timedelta(days=30)

# Convert to timestamp (milliseconds)
expiry_timestamp_1 = int(expiry_time_1.timestamp() * 1000)

print(expiry_timestamp_1)  # Use this value in your payload


# add_inbound(0, 'test', '2month', expiry_timestamp_2)


def add_client(inbound_id, name, time):

    login_url = "https://s1.arganas.com:2053/login"
    credentials = {
        "username": "shayan",  # Replace with actual username
        "password": "sh1sh2sh3"   # Replace with actual password
    }


    session = requests.Session()

    # Login to the server
    try:
        response = session.post(login_url, data=credentials)
        if response.status_code == 200:
            print("Login successful!")
            cookies = session.cookies.get_dict()
            print(f"Cookies: {cookies}")
        else:
            print(f"Login failed. Status Code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print("An error occurred during login:", e)
            

    list_inbounds_url = f"https://s1.arganas.com:2053/panel/api/inbounds/get/{inbound_id}"


    # Check the current list of inbounds and gather existing ports
    try:
        inbounds_response = session.get(list_inbounds_url)
        if inbounds_response.status_code == 200:
            print("Raw response from inbounds list:")
            port = int(inbounds_response.json()['obj']['port'])
            protocol = inbounds_response.json()['obj']['protocol'] 
            data = inbounds_response.json()
            stream_settings = json.loads(data['obj']['streamSettings'])   # Print the raw response content
            security = stream_settings['security']
            
            print(port)
            print(protocol)
            print(security)

    except requests.exceptions.RequestException as e:
        print("An error occurred while fetching inbounds:", e)
  

    new_client_id = str(uuid.uuid4())  # Generate a new UUID for the client


    settings = {
        "clients": [{
            "id": new_client_id,
            "alterId": 0,
            "email": f"{name}{new_client_id}@gmail.com",
            "limitIp": 2,
            "totalGB": 42949672960,
            "expiryTime": time,  # Example expiry time in milliseconds
            "enable": True,
            "tgId": "",
            "subId": ""
        }],
        "decryption": "none",
        "fallbacks": []

        }

    client_payload = {
        "id": int(inbound_id),
        "settings": json.dumps(settings)
    }

    # Step 4: Send the POST request to add the client with the cookies
    add_client_url = "https://s1.arganas.com:2053/panel/api/inbounds/addClient"

    try:
        
        # Send the request with the cookie in the headers
        response = session.post(add_client_url, json=client_payload, cookies=cookies)

        # Check response status and print details
        print(f"Response Status Code: {response.status_code}")
        print(f"Raw Response Text: {response.text}")
        if response.status_code == 200:
            if response.text.strip():
                inbound_data = response.json()
                print("Parsed Response JSON:", inbound_data)
            else:
                print("Success, but the server returned an empty response.")
        else:
            print(f"Failed to add client. Status Code: {response.status_code}")

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")

        if response.status_code == 200:
            print("Response Text:", response.text)  # Print the raw response text to inspect it
        else:
            print("Failed to add client. No data returned.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while adding client: {e}")

    path ='/'
    config_url = f"vless://{new_client_id}@s1.arganas.com:443?type=ws&path=%2F&host=s1.arganas.com&security=tls&fp=chrome&alpn=http%2F1.1#{name}{new_client_id}"
    print(config_url)

    return config_url



