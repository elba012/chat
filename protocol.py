import time

LENGTH_FIELD_SIZE = 2

COMMANDS = {"text": 1, "Admin": 2, "Kick": 3, "Mute": 4, "quit": 0}


# create server command for members list (2), mute (3)
def create_msg_server(command, data):
    length = str(len(data)).zfill(LENGTH_FIELD_SIZE)
    return (str(command) + length + data).encode()


# create server message to send to all the members (starting with 1)
def create_msg(sender, data):
    current_time = time.strftime("%H:%M")
    message = current_time + " " + sender + ": " + data
    length = str(len(message)).zfill(LENGTH_FIELD_SIZE)
    return ("1" + length + message).encode()


# create
def create_msg_client(sender, command, data, send_to=None):
    if command != "private":
        command = COMMANDS.get(command)
        length = str(len(data)).zfill(LENGTH_FIELD_SIZE)
        return (str(len(sender)) + sender + str(command) + length + data).encode()
    length = str(len(data)).zfill(LENGTH_FIELD_SIZE)
    return (str(len(sender)) + sender + "5" + str(len(send_to)) + send_to + length + data).encode()


def get_msg_client(my_socket, length_field_size=LENGTH_FIELD_SIZE):
    """
    Extract message from protocol, without the length field.
    return list of element include the message and command
    """
    command = my_socket.recv(1).decode()
    length = my_socket.recv(length_field_size).decode()
    message = my_socket.recv(int(length)).decode()
    return [command, message]


def get_msg(my_socket, length_field_size=LENGTH_FIELD_SIZE):
    """
    Extract message from protocol, without the length field.
    return list of element include the message and command
    """
    length_nickname = my_socket.recv(1).decode()
    print(length_nickname)
    nickname = my_socket.recv(int(length_nickname)).decode()
    print(nickname)
    command = my_socket.recv(1).decode()
    print(command)
    if 0 <= int(command) <= 4:
        length_data = my_socket.recv(length_field_size).decode()
        data = my_socket.recv(int(length_data)).decode()
        return [nickname, command, data]
    else:
        length_nickname2 = my_socket.recv(1).decode()
        nickname2 = my_socket.recv(int(length_nickname2)).decode()
        length_data = my_socket.recv(length_field_size).decode()
        data = my_socket.recv(int(length_data)).decode()
        return [nickname, command, nickname2, data]
