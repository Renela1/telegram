import paramiko
import json

def fetch_xui_clients_via_ssh(server_ip, username, password, seller_id):
    try:
        # SSH connection setup
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_ip, username=username, password=password)

        # SQLite command to extract clients from JSON field
        command = """ sqlite3 /etc/x-ui/x-ui.db "SELECT json_extract(settings, '$.clients') FROM inbounds;" """

        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode().strip()
        ssh.close()

        if output:
            clients_per_inbound = output.splitlines()
            all_clients = []
            returned_clients = []

            for item in clients_per_inbound:
                try:
                    clients = json.loads(item)
                    all_clients.extend(clients)
                except json.JSONDecodeError:
                    continue  # Skip any rows that fail to parse

            print("✅ Extracted Clients:")
            for client in all_clients:
                if seller_id in client.get('email', ''):
                    returned_clients.append(client.get('email'))

            return returned_clients
        else:
            print("No client data found.")
            return []

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


# Example usage
client = fetch_xui_clients_via_ssh("8.211.55.81", "root", "Shayan1@pass", "6001068123")

print(str(client))

