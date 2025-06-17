import socket
import threading

HOST = '127.0.0.1'
PORT = 6969
client = None

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))
        print(f"Connected to server in {HOST}:{PORT}")
    except Exception as e:
        print(f"Unable to connect to server in {HOST}:{PORT}, error: {e}")
        print(f"Exiting...")
        exit(0)

    communicate_to_server(client)


def communicate_to_server(client):
    username = input('Enter username: ')

    if username == '':
        print('Username can not be empty')
        print(f"Exiting...")
        exit(0)

    client.sendall(username.encode())

    threading.Thread(target=listen_for_message, args=(client, )).start()

    send_message(client)

def listen_for_message(client):
    while True:
        message = client.recv(2048).decode('utf-8')

        if message == '':
            continue

        username = message.split('~')[0]
        content = message.split('~')[1]

        print(f"[{username}] ~ {content}")

def send_message(client):
    while True:
        message = input('Message: ')

        if message == '':
            print('Message cannot be empty')
            continue

        client.sendall(message.encode())

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Keyboard interrupt')
    except Exception as e:
        print(f'Unexpected error: {e}')

    if client:
        print('Closing client')
        client.close()
    exit(0)