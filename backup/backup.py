import routeros_api


ROUTER_IP = "S3dl.andromobile.online"
PORT = 8000 
USERNAME = "maza7380"
PASSWORD = "maza7380"


try:
  
    api = routeros_api.RouterOsApiPool(
        ROUTER_IP, username=USERNAME, password=PASSWORD, port=PORT
    )
    conn = api.get_api()


    commands = {
        "Interfaces": "/interface print",
        "IP Addresses": "/ip address print",
        "Firewall Rules": "/ip firewall filter print",
        "NAT Rules": "/ip firewall nat print",
        "Routes": "/ip route print",
        "PPP Users": "/ppp secret print",
        "DHCP Leases": "/ip dhcp-server lease print",
        "Wireless Profiles": "/interface wireless security-profiles print",
        "Users": "/user print"
    }


    with open("mikrotik_backup.rsc", "w") as file:
        file.write("# MikroTik Auto-Generated Backup Script\n\n")

        for section, command in commands.items():
            file.write(f"\n# --- {section} ---\n")
            results = conn.get_resource(command).get()
            
            for entry in results:
        
                line = " ".join([f"{key}={value}" for key, value in entry.items()])
                if line:
                    file.write(f"{command.replace(' print', ' add')} {line}\n")

        file.write("\n# End of Backup\n")

    print("MikroTik backup saved as 'mikrotik_backup.rsc' successfully!")

    # Close API connection
    api.disconnect()

except Exception as e:
    print(f"Error: {e}")
