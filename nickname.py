import tkinter as tk
from tkinter import messagebox

# create tkinter window for get nickname
def get_nickname():
    def save_nickname():
        input_nickname = nickname_entry.get()
        if 1 <= len(input_nickname) <= 9 and not input_nickname.startswith('@') and not input_nickname.startswith('!'):
            nickname_window.destroy()
            result.set(input_nickname)
        else:
            messagebox.showerror("Invalid Nickname", "pls write a valid nickname")

    nickname_window = tk.Tk()
    nickname_window.title("Nickname Entry")

    nickname_label = tk.Label(nickname_window, text="Enter your nickname (1-9 letters, not starting with @ and !):")
    nickname_label.pack(pady=10)

    nickname_entry = tk.Entry(nickname_window)
    nickname_entry.pack()

    submit_button = tk.Button(nickname_window, text="Submit", command=save_nickname)
    submit_button.pack()

    result = tk.StringVar()

    nickname_window.mainloop()

    return result.get()
