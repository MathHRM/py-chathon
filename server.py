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
    except:
        print(f'Unable to bind to port {HOST}:{PORT}')

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
            print(f"Receive empty response from user {username}")
            continue

        final_msg = username + '~' + response
        send_messages_to_all(final_msg)

def send_messages_to_all(message):
    for user in active_clients:
        send_message_to_client(user[1], message)

def send_message_to_client(client, message):
    client.sendall(message.encode())


if __name__ == '__main__':
    main()