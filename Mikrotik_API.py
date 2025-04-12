import routeros_api

# MikroTik Credentials
MIKROTIK_HOST = "S3dl.andromobile.online"
PORT = 8000  # Change if needed
USERNAME = "maza7380"
PASSWORD = "maza7380"

# Establish Connection
try:
    connection = routeros_api.RouterOsApiPool(
        host=MIKROTIK_HOST,
        username=USERNAME,
        password=PASSWORD,
        port=PORT,
        plaintext_login=True  # Set to False if using encryption
    )
    
    api = connection.get_api()
    print("✅ Connected to MikroTik API!")

except Exception as e:
    print(f"❌ Connection Error: {e}")


try:
    profile_bindings = api.get_resource("/interface/ovpn-server")
    bindings = profile_bindings.get()

    print("\n🔹 Profile Binding Response:")
    for binding in bindings:
        print(binding)  # Print each binding dictionary

except Exception as e:
    print(f"❌ Error: {e}")


try:

    # User details
    user_data = {
        "name": "AAA111",  # Username
        "password": "mypassword",  # User Password
        "group": "default",  # User Group
        "shared-users": "1",  # Number of concurrent logins
    }

    # Add user in User Manager
    user_manager = api.get_resource('/user-manager/user')
    response = user_manager.add(**user_data)

    print("✅ User added successfully:", response)

    connection.disconnect()

except Exception as e:
    print("❌ Error:", str(e))


user = user_manager.get(name="testuser")  # Replace with the username you added
if user:
    print("✅ User exists:", user)
else:
    print("❌ User not found")


USER_ID = "*CD8"  
PROFILE_ID = "*1"  

try:

    # Access the profile binding section
    binding_manager = api.get_resource('/user-manager/user-profile')

    # Assign Profile to User
    binding_manager.add(user=USER_ID, profile=PROFILE_ID)
    print(f"✅ Profile '{PROFILE_ID}' assigned to user '{USER_ID}' successfully.")

    connection.disconnect()

except Exception as e:
    print("❌ Error:", str(e))

users = user_manager.get(name=USERNAME)
print("User Data:", users)

session_manager = api.get_resource('/user-manager/session')
sessions = session_manager.get()

USER_TO_CHECK = "ppp1"

ppp_secrets = api.get_resource('/ppp/secret').get()
user_found = any(user['name'] == USER_TO_CHECK for user in ppp_secrets)

if user_found:
    print(f"User '{USER_TO_CHECK}' exists in /ppp/secret.")
else:
    print(f"User '{USER_TO_CHECK}' is NOT in /ppp/secret.")


for user in ppp_secrets:
    if user['name'] == USER_TO_CHECK:
        print(f"User '{USER_TO_CHECK}' has profile: {user['profile']}")


services = api.get_resource('/ip/service').get()
ovpn_service = next((s for s in services if s['name'] == 'ovpn'), None)

if ovpn_service and ovpn_service['disabled'] == 'false':
    print(f"OVPN Server is running on port {ovpn_service['port']}.")
else:
    print("OVPN Server is NOT running.")


try:

    api_resource = api.get_resource('/user')

    # Get all system users
    users = api_resource.get()

    # Print user list
    print("MikroTik System Users:")
    for user in users:
        print(f"- Username: {user['name']}, Group: {user.get('group', 'Unknown')}")

except Exception as e:
    print(f"Error: {e}")

import routeros_api


NEW_ADMIN = "myadmin"
NEW_PASS = "SuperSecurePass"

try:

    user_resource = api.get_resource('/user')

    user_resource.add(name='myadmin', password='SuperSecurePass', group="full")

    print(f"✅ New admin user '{NEW_ADMIN}' created successfully!")

except Exception as e:
    print(f"Error: {e}")


import routeros_api


try:
    # Connect to MikroTik
    api = routeros_api.RouterOsApiPool(        host=MIKROTIK_HOST,
        username=USERNAME,
        password=PASSWORD,
        port=PORT,
        plaintext_login=True )
    
    api_conn = api.get_api()

    # Run export command directly
    api_conn.get_resource('/').call('export', {'file': 'config_backup'})

    print("✅ Configuration export started. Download 'config_backup.rsc' from Winbox > Files.")

except Exception as e:
    print(f"Error: {e}")


try:
    api = routeros_api.RouterOsApiPool(host=MIKROTIK_HOST, username=USERNAME, password=PASSWORD, port=PORT, plaintext_login=True)

    conn = api.get_api()


    resources = {

            "Interfaces": conn.get_resource('/interface'),
            "IP Addresses": conn.get_resource('/ip/address'),
            "DNS": conn.get_resource('/ip/dns'),
            "Firewall Rules": conn.get_resource('/ip/firewall/filter'),
            "NAT Rules": conn.get_resource('/ip/firewall/nat'),
            "Mangle": conn.get_resource('/ip/firewall/mangle'),
            "NAT Rules": conn.get_resource('/ip/firewall/service-port'),
            "NAT Rules": conn.get_resource('/ip/firewall/address-list'),
            "Routes": conn.get_resource('/ip/route'),
            "PPP Users": conn.get_resource('/ppp/secret'),
            "DHCP Leases": conn.get_resource('/ip/dhcp-server/lease'),
            "Wireless Profiles": conn.get_resource('/interface/ovpn-server'),
            "Users": conn.get_resource('/user'),
            "usermanager": conn.get_resource('/user-manager/profile'),
            "Profile": conn.get_resource('/ppp/profile'),
            "limit-profiles": conn.get_resource('user-manager/profile'),
            "Routhers": conn.get_resource('user-manager/router'),
            "Limits": conn.get_resource('user-manager/limitation'),
            "Ethernet": conn.get_resource('interface/ethernet'),
            "Radius": conn.get_resource('radius'),
            "Console": conn.get_resource('system/console'),
            "Packages": conn.get_resource('system/package'),
            "GRE": conn.get_resource('interface/gre'),
        }


    with open("mikrotik_backup2.rsc", "w") as file:
        file.write("# MikroTik Auto-Generated Backup Script\n\n")

        for section, resource in resources.items():
            file.write(f"\n# --- {section} ---\n")
            results = resource.get()

            for entry in results:

                line = " ".join([f"{key}={value}" for key, value in entry.items()])
                if line:
                    file.write(f"/{resource.path.replace('/', ' ')} add {line}\n")

        file.write("\n# End of Backup\n")

    print("MikroTik backup saved as 'mikrotik_backup2.rsc' successfully!")

    # Close API connection
    api.disconnect()

except Exception as e:
    print(f"Error: {e}")