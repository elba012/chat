import socket
import threading
import protocol

host = '0.0.0.0'
port = 1234

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print("server is up and running")

# Lists For Clients and Their Nicknames
clients = []
nicknames = []
admins = ["tal", "amit"]


# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)


# the function handle the data received from the clients
def handle_data(data):
    if data[1] == '1':
        message = protocol.create_msg(data[0], data[2])
        broadcast(message)
    elif data[1] == '2':  # make admin
        nickname = data[2]
        index = nicknames.index(nickname)
        if nickname.startswith('@'):
            message = protocol.create_msg("server", f"{nickname} already admin")
            index1 = nicknames.index(data[0])
            clients[index1].send(message)
        else:
            nicknames[index] = "@" + nickname
            broadcast(protocol.create_msg_server(2, ":".join(nicknames)))
            message = protocol.create_msg("server", f"{nickname} is now admin")
            broadcast(message)
    elif data[1] == '3':  # kick someone
        nickname = data[2]
        index = nicknames.index(nickname)
        message = protocol.create_msg("server", f"{nickname} has been kick from the chat!")
        broadcast(message)
        client = clients[index]
        clients.remove(client)
        client.close()
        nicknames.remove(nickname)
        new_members = ":".join(nicknames)
        print(new_members)
        broadcast(protocol.create_msg_server(2, new_members))
    elif data[1] == '4':  # mute or unmute someone
        index1 = nicknames.index(data[2])
        clients[index1].send(protocol.create_msg_server(3, ""))
    elif data[1] == '5':  # private message
        index = nicknames.index(data[0])
        index1 = nicknames.index(data[2])
        message = protocol.create_msg("!"+data[0], data[3])
        clients[index].send(message)
        clients[index1].send(message)
    elif data[1] == '0':  # quit
        index = nicknames.index(data[2])
        client = clients[index]
        clients.remove(client)
        client.close()
        nicknames.remove(data[2])
        message = protocol.create_msg("server", f"{data[2]} has left the chat!")
        print(len(clients))
        broadcast(message)


# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            data = protocol.get_msg(client)
            print(data)
            handle_data(data)
        except Exception as e:
            # Removing And Closing Clients
            print(e)
            message = protocol.create_msg("server", "try to send other message")
            client.send(message)
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                message = protocol.create_msg("server", '{} left!'.format(nickname))
                broadcast(message)
                nicknames.remove(nickname)
                break


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        length = client.recv(1).decode()
        nickname = client.recv(int(length)).decode()
        if nickname in nicknames or "@" + nickname in nicknames:
            client.send('no'.encode())
        else:
            client.send('ok'.encode())
            nicknames.append(nickname)
            clients.append(client)
            if nickname in admins and not nickname.startswith("@"):
                index = nicknames.index(nickname)
                nicknames[index] = "@" + nickname
            broadcast(protocol.create_msg_server(2, ":".join(nicknames)))
            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname))
            message = protocol.create_msg("server", f"{nickname} joined!")
            broadcast(message)

            # Start Handling Thread For Client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()


receive()
