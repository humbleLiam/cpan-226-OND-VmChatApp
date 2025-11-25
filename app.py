import tkinter as tk
from gui import ChatGUI
from connection import Connection

def main():
    peer_ip = "192.168.100.4"  # Replace with discovery logic later
    conn = Connection(peer_ip, 5000)

    root = tk.Tk()
    app = ChatGUI(root, conn)
    root.mainloop()

if __name__ == "__main__":
    main()
