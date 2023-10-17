import socket
import threading
import protocol
from styles import widget_color, text_color, background_color
import styles
from nickname import get_nickname  # Import the get_nickname function
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Get the nickname using the Tkinter function
nickname = ''
while nickname == '':
    nickname = get_nickname()

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 1234))
# check if nickname already exist
client.send((str(len(nickname)) + nickname).encode())
message1 = client.recv(2).decode()
while message1 != "ok":
    messagebox.showerror("Invalid Nickname", "nickname already exist")
    nickname = get_nickname()
    client.send((str(len(nickname)) + nickname).encode())
    message1 = client.recv(2).decode()

is_mute = False
is_admin = False
# Create the main application window
window = tk.Tk()
window.title("chat")
window.resizable(False, False)  # Prevent window resizing
window.configure(bg=background_color)

# text label for nickname
user_label = ttk.Label(window, text="hey " + nickname, font=("Helvetica", 24, "bold"), foreground=text_color)
user_label .pack(padx=20, pady=10)

# Call the configure_styles function from style_config
styles.configure_styles()
# Create a frame for the chat display area and entry field
chat_entry_frame = ttk.Frame(window)
chat_entry_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True, side=tk.LEFT)

# Create a text widget to display the chat
chat_box = tk.Text(chat_entry_frame, state=tk.DISABLED, wrap=tk.WORD, background=widget_color, foreground=text_color)
chat_box.pack(fill=tk.BOTH, expand=True)

# create menu bar
options = ["everyone"]
option_var = tk.StringVar(chat_entry_frame)
option_var.set(options[0])  # Set default option

option_menu = ttk.OptionMenu(chat_entry_frame, option_var, *options)
option_menu.pack(pady=20, side=tk.LEFT, padx=(5, 5))


# Listening to Server and handle commands
def receive():
    global is_mute
    while True:
        try:
            # Receive Message From Server
            print("here")
            command = protocol.get_msg_client(client)
            print(command)
            if command[0] == '1':
                chat_box.config(state=tk.NORMAL)
                chat_box.insert(tk.END, command[1] + "\n")
                chat_box.see(tk.END)  # Scroll to the bottom
                chat_box.config(state=tk.DISABLED)
                entry.delete(0, tk.END)
            elif command[0] == '2':  # active members changed
                check_member(command[1])
            elif command[0] == '3':  # client has been muted
                is_mute = not is_mute
                if is_mute:
                    messagebox.showinfo("message", "you have been muted")
                else:
                    messagebox.showinfo("message", "you are no longer muted")

        except Exception as e:
            print(e)
            print("there was an error, closing...")
            client.close()  # close the connection with the server
            window.destroy()
            exit()


#  check if the member is admin or if the client has been kicked
def check_member(members):
    global is_admin, nickname
    members = members.split(":")
    if nickname not in members and "@" + nickname not in members:
        send_message("you have been kicked", nickname)
        messagebox.showinfo("message", "you have been kicked")
        client.close()
        window.destroy()
        return
    if "@" + nickname in members and not nickname.startswith("@"):
        is_admin = True
        nickname = "@" + nickname
    else:
        if not nickname.startswith("@"):
            is_admin = False

    update_option_menu(members)


#  create a frame for the members
members_frame = ttk.Frame(window)
members_frame.pack(padx=20, pady=20, fill=tk.BOTH, side=tk.RIGHT)

# Create action buttons
kick_button = ttk.Button(members_frame, text="Kick", command=lambda: on_button_click("Kick"))
mute_button = ttk.Button(members_frame, text="Mute", command=lambda: on_button_click("Mute"))
admin_button = ttk.Button(members_frame, text="Make Admin", command=lambda: on_button_click("Admin"))
kick_button.pack(pady=5, fill=tk.BOTH, side=tk.BOTTOM)
mute_button.pack(pady=5, fill=tk.BOTH, side=tk.BOTTOM)
admin_button.pack(pady=5, fill=tk.BOTH, side=tk.BOTTOM)


#  update the button visibility if the user is admin
def update_button_visibility():
    global is_admin
    if is_admin:
        kick_button.pack(pady=5, fill=tk.BOTH, side=tk.BOTTOM)
        mute_button.pack(pady=5, fill=tk.BOTH, side=tk.BOTTOM)
        admin_button.pack(pady=5, fill=tk.BOTH, side=tk.BOTTOM)
    else:
        kick_button.pack_forget()
        mute_button.pack_forget()
        admin_button.pack_forget()


#  update option menu and members listbox after an event
def update_option_menu(members):
    global option_menu, entry, members_listbox, options
    options = ["everyone"]
    for member in members:
        options.append(member)
    option_menu.destroy()  # Destroy the old option_menu
    option_menu = ttk.OptionMenu(chat_entry_frame, option_var, options[0], *options)  # Recreate the option_menu
    option_menu.pack(pady=20, side=tk.LEFT, padx=(5, 5))
    entry.destroy()
    entry = ttk.Entry(chat_entry_frame, font=("Helvetica", 12))
    entry.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(5, 5))
    members_listbox.destroy()
    members_listbox = tk.Listbox(members_frame, background=widget_color, foreground=text_color, font=("Helvetica", 12))
    members_listbox.pack(fill=tk.BOTH, expand=True)

    # Insert members from the options list
    for member in options:
        if member != "everyone":
            members_listbox.insert(tk.END, member)
    update_button_visibility()


#  function that send messages to the server
def send_message(message, send_to=""):
    global is_mute, options
    if message == "quit":
        message = protocol.create_msg_client(nickname, "quit", nickname)
        client.send(message)
        exit()
    elif message == "view-managers":
        admins = [member for member in options if member.startswith("@")]
        message = protocol.create_msg_client(nickname, "private",  f'[{",".join(admins)}]', nickname)
        client.send(message)
    else:
        if not is_mute:
            if message:
                send_to = option_var.get() if send_to == "" else send_to
                if send_to == "everyone":
                    message = protocol.create_msg_client(nickname, "text", message)
                else:
                    message = protocol.create_msg_client(nickname, "private", message, send_to)
                print(message)
                client.send(message)
            else:
                send_message("you need to write something")
        else:
            message = protocol.create_msg_client(nickname, "private", "you can't send message when mute", nickname)
            client.send(message)


#  send action messages to the server (like kick, mute or admin)
def on_button_click(action):
    try:
        selected_member = members_listbox.get(members_listbox.curselection())
        if selected_member == nickname or selected_member == "@" + nickname:
            message = protocol.create_msg_client(nickname, "private", "you can't choose yourself", nickname)
        else:
            message = protocol.create_msg_client(nickname, action, selected_member)
        client.send(message)
    except tk.TclError:
        print("you need to select a member")


# Starting Threads For Listening
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Create an entry widget for typing messages
entry = ttk.Entry(chat_entry_frame, font=("Helvetica", 12))
entry.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(5, 5))

# Create a send button
send_button = ttk.Button(chat_entry_frame, text="Send", command=lambda: send_message(entry.get()))
send_button.pack(side=tk.RIGHT, padx=(0, 5))

# Create a label for active members
members_label = ttk.Label(members_frame, text="Active Members", font=("Helvetica", 16, "bold"), foreground=text_color)
members_label.pack(pady=10)

# create list for active members with a listbox
members_listbox = tk.Listbox(members_frame, background=styles.widget_color, foreground=text_color,
                             font=("Helvetica", 12))
members_listbox.pack(fill=tk.BOTH, expand=True)

window.mainloop()

