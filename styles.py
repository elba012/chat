from tkinter import ttk

# Define color
background_color = "#61677A"  # window background
widget_color = "#EEEEEE"  # background for frames
text_color = "#222831"  # text color


def configure_styles():
    style = ttk.Style()
    # Configure style elements
    style.configure("TFrame", background=background_color)
    style.configure("TLabel", background=background_color, foreground=text_color, font=("Helvetica", 14))
    style.configure("TButton", foreground=text_color)
    style.configure("TEntry", fieldbackground=widget_color, foreground=text_color, font=("Helvetica", 12))


