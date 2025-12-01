import tkinter as tk
from gui import ChatGUI
from connection import Connection
from database import ChatDatabase

def main():

    db =ChatDatabase("chat_history.db")
    peer_ip = "192.168.100.4"  # Replace with discovery logic later
    conn = Connection(peer_ip, 5000)

    root = tk.Tk()
    app = ChatGUI(root, conn,db,peer_ip)
 
    db.add_contact(peer_ip,f"Peer({peer_ip})")
    app.add_contact(f"Peer ({peer_ip})")
    app.load_chat_history(peer_ip)

    app.set_input_enabled(False)
    app.update_connection_status("--Connecting--")

    def waitForConnection():
        connected = conn.confirmConnection()
        if connected:

            app.set_input_enabled(True)
            app.update
        else:
            root.after(200,waitForConnection)

    def onClosing():
        db.close()
        conn.close()
        root.destroy()

    waitForConnection()
    root.protocol("WM_DELETE_WINDOW",onClosing)
    root.mainloop()


if __name__ == "__main__":
    main()
