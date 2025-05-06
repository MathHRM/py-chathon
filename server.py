import socket
import threading
import re
from enum import Enum

HOST = '127.0.0.1'
PORT = 1234
LISTENER_LIMIT = 5
active_clients = []
store_messages = []
server = None

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

class MessageOriginType(Enum):
    USER_MESSAGE = 0
    COMMAND = 1

def client_handler(client):
    username = ''

    while True:
        username = client.recv(2048).decode('utf-8')

        if username == '':
            print("Client name is empty")
            continue

        active_clients.append((username, client))
        print(f"User {username} joined the chat")

        send_message_to_all(username, 'Welcome to the server')
        break

    threading.Thread(target=listen_for_message, args=(username, client, )).start()

def listen_for_message(username, client):
    while True:
        response = client.recv(2048).decode('utf-8')

        if response == '':
            continue

        if re.match(r"^/.\b", response):
            process_command(username, client, substring_after(response, '/'))
            continue

        send_message_to_all(username, response)

def process_command(username, client, commandRef):
    try:
        match commandRef:
            case 'whoami': whoami(username, client)
            case 'users': show_users_in_chat(username, client)

            case _: command_not_exists(username, client)
    except:
        error_executing_command(client, username)

def send_message_to_all(username, message):
    for user in active_clients:
        client = user[1]
        save_and_send_message(client, username, message)

def save_and_send_message(client, username, message, origin = MessageOriginType.USER_MESSAGE):
    save_message(username, message, origin)

    message = format_message(username, message)
    client.sendall(message.encode())

def save_message(username, message, origin):
    store_messages.append({
        'username': username,
        'message': message,
        'origin': origin
    })

def format_message(username, message):
    return f"{username}~{message}"

def substring_after(s, delim):
    return s.partition(delim)[2]



# COMMANDS

def whoami(username, client):
    save_and_send_message(client, username, f'You are nothing, but your name is {username}', MessageOriginType.COMMAND)

def show_users_in_chat(username, client):
    usersnames = [user[0] for user in active_clients]
    save_and_send_message(client, username, f'Users in chat: {usersnames}', MessageOriginType.COMMAND)

def error_executing_command(client, username):
    save_and_send_message(client, username, f'Error executing command', MessageOriginType.COMMAND)

def command_not_exists(username, client):
    save_and_send_message(client, username, f'Command does not exist', MessageOriginType.COMMAND)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        if server:
            print('Server closed')
            server.close()

        print(store_messages)
        exit(0)
