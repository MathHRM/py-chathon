import socket
import threading

HOST = '127.0.0.1'
PORT = 1234
LISTENER_LIMIT = 5
active_clients = []

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((HOST, PORT))
        print(f'Running server in {HOST}:{PORT}')
    except Exception as exception:
        print(f'Unable to bind to port {HOST}:{PORT}. Error: {exception}')

    server.listen(LISTENER_LIMIT)

    while True:
        client, address = server.accept()
        print(f"Successfully connected to client {address[0]}:{address[1]}")

        threading.Thread(target=client_handler, args=(client, )).start()

def client_handler(client):
    username = ''

    while True:
        username = client.recv(2048).decode('utf-8')

        if username == '':
            print("Client name is empty")
            continue
        
        active_clients.append((username, client))
        break

    threading.Thread(target=listen_for_message, args=(username, client, )).start()
            
def listen_for_message(username, client):
    while True:
        response = client.recv(2048).decode('utf-8')

        if response == '':
            continue

        if response.startswith('/'):
            process_command(username, client, substring_after(response, '/'))
            continue

        final_msg = format_message(username, response)
        send_messages_to_all(final_msg)

def process_command(username, client, commandRef):
    try:
        match commandRef:
            case 'whoami': whoami(username, client)
            
            case _: command_not_exists(username, client)
    except:
        send_message_to_client(client, format_message(username, 'Command does not exist'))

def send_messages_to_all(message):
    for user in active_clients:
        send_message_to_client(user[1], message)

def send_message_to_client(client, message):
    client.sendall(message.encode())

def format_message(username, message):
    return f"{username}~{message}"

def substring_after(s, delim):
    return s.partition(delim)[2]


# commands

def whoami(username, client):
    send_message_to_client(client, format_message(username, f'You are nothing, but your name is {username}'))

def command_not_exists(username, client):
    send_message_to_client(client, format_message(username, f'Command does not exist'))

if __name__ == '__main__':
    main()