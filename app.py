import tkinter as tk
from gui import ChatGUI
from connection import Connection
from database import ChatDatabase
import traceback  # ADD THIS

def main():
    try:  # ADD THIS
        db = ChatDatabase("chat_history.db")
        peer_ip = "192.168.100.4"
        conn = Connection(peer_ip, 5000)

        root = tk.Tk()
        app = ChatGUI(root, conn, db, peer_ip)
    
        db.add_contact(peer_ip, f"Peer ({peer_ip})")
        app.add_contact(f"Peer ({peer_ip})")
        def waitForConnection():
            if conn.isConnected:
                app.load_chat_history(peer_ip)
            else:
                root.after(200,waitForConnection)

        def onClosing():
            db.close()
            conn.close()
            root.destroy()

            
        waitForConnection()
        root.protocol("WM_DELETE_WINDOW", onClosing)
        root.mainloop()
    
    except Exception as e:  # ADD THIS
        print(f"ERROR: {e}")  # ADD THIS
        traceback.print_exc()  # ADD THIS
        input("Press Enter to exit...")  # ADD THIS

if __name__ == "__main__":
    main()