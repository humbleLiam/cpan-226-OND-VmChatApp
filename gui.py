import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime


class ChatGUI:
    def __init__(self, root, connection, database=None, peer_ip=None):
        self.root = root
        self.conn = connection
        self.db = database
        self.peer_ip = peer_ip
        self.root.title("Chat Interface")
        self.root.geometry("800x600")
        self.root.configure(bg="#1f2933")

        # Track contacts & current selection
        self.contacts = []          # start with NO sample contacts
        self.current_contact = None
        self.last_message_date = None

        # Layout config
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # -------- Left: Contact list sidebar --------
        sidebar = tk.Frame(self.root, bg="#111827", width=200)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        sidebar_title = tk.Label(
            sidebar,
            text="Contacts",
            bg="#111827",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=10
        )
        sidebar_title.pack(fill=tk.X)

        self.contact_listbox = tk.Listbox(
            sidebar,
            bg="#1f2933",
            fg="white",
            selectbackground="#10b981",
            selectforeground="black",
            bd=0,
            highlightthickness=0,
            font=("Arial", 10)
        )
        self.contact_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.contact_listbox.bind("<<ListboxSelect>>", self.on_contact_select)

        # -------- Right: Main chat area --------
        main_area = tk.Frame(self.root, bg="#e5e7eb")
        main_area.grid(row=0, column=1, sticky="nsew")
        main_area.grid_rowconfigure(1, weight=1)
        main_area.grid_columnconfigure(0, weight=1)

        # Top bar: just contact name
        header = tk.Frame(main_area, bg="#111827", height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        self.contact_name_label = tk.Label(
            header,
            text="No contact selected",
            bg="#111827",
            fg="white",
            font=("Arial", 12, "bold")
        )
        self.contact_name_label.pack(anchor="w", padx=15, pady=(15, 0))

        # Chat display frame
        chat_frame = tk.Frame(main_area, bg="#e5e7eb")
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            state="disabled",
            font=("Arial", 10),
            bg="#e5e7eb",
            bd=0,
            relief=tk.FLAT
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Styling tags
        self.chat_display.tag_config(
            "user_bubble",
            background="#DCF8C6",   # right side (your messages)
            lmargin1=150,
            lmargin2=150,
            rmargin=10,
            spacing1=5,
            spacing3=5
        )
        self.chat_display.tag_config(
            "peer_bubble",
            background="#FFFFFF",   # left side (incoming)
            lmargin1=10,
            lmargin2=10,
            rmargin=150,
            spacing1=5,
            spacing3=5
        )
        self.chat_display.tag_config(
            "timestamp_left",
            foreground="#6b7280",
            font=("Arial", 8),
            lmargin1=10,
            lmargin2=10,
            spacing1=0,
            spacing3=8
        )
        self.chat_display.tag_config(
            "timestamp_right",
            foreground="#6b7280",
            font=("Arial", 8),
            lmargin1=150,
            lmargin2=150,
            spacing1=0,
            spacing3=8,
            justify="right"
        )
        self.chat_display.tag_config(
            "date_separator",
            foreground="#9ca3af",
            font=("Arial", 9, "italic"),
            justify="center",
            spacing1=15,
            spacing3=10
        )

        # Bottom input area
        input_frame = tk.Frame(main_area, bg="#e5e7eb")
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)

        self.message_input = tk.Entry(input_frame, font=("Arial", 11))
        self.message_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.message_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#10b981",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            bd=0,
            activebackground="#059669",
            activeforeground="white",
            cursor="hand2"
        )
        self.send_button.grid(row=0, column=1, padx=(5, 0))

        # Start polling incoming messages
        self.poll_incoming()

    # ---------- Contacts ----------

    def add_contact(self, name: str):
        """Add a contact to the list (no duplicates). Call this manually from your code."""
        if name not in self.contacts:
            self.contacts.append(name)
            self.contact_listbox.insert(tk.END, name)
            # If no contact selected yet, select this one
            if self.current_contact is None:
                self.current_contact = name
                self.contact_listbox.selection_clear(0, tk.END)
                self.contact_listbox.selection_set(tk.END)
                self.contact_name_label.config(text=name)

    def on_contact_select(self, event):
        selection = self.contact_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        self.current_contact = self.contacts[index]
        self.contact_name_label.config(text=self.current_contact)

    # ---------- Messages ----------

    def add_message(self, message, sender="user", save_to_db =True):
        self.chat_display.config(state="normal")

        now = datetime.now()
        time_str = now.strftime("%I:%M %p").lstrip("0")  # e.g. "2:51 PM"
        date_str = now.strftime("%B %d, %Y")

        # Date separator once per day
        if date_str != self.last_message_date:
            if self.chat_display.index("end-1c") != "1.0":
                self.chat_display.insert(tk.END, "\n")
            self.chat_display.insert(tk.END, f"{date_str}\n", "date_separator")
            self.last_message_date = date_str

        if sender == "user":
            bubble_tag = "user_bubble"
            ts_tag = "timestamp_right"
            name = "You"
            db_sender = "me"
        else:  # "peer"
            bubble_tag = "peer_bubble"
            ts_tag = "timestamp_left"
            name = self.current_contact if self.current_contact else "Peer"
            db_sender ="peer"
            
        if save_to_db and self.db and self.peer_ip:
            self.db.add_message(self.peer_ip, message, db_sender)

        # Name above bubble
        self.chat_display.insert(tk.END, f"{name}\n", bubble_tag)
        # Message bubble
        self.chat_display.insert(tk.END, f"{message}\n", bubble_tag)
        # Timestamp under bubble
        self.chat_display.insert(tk.END, f"{time_str}\n", ts_tag)
        self.chat_display.insert(tk.END, "\n")

        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def send_message(self, event=None):
        message = self.message_input.get().strip()
        if message:
            self.add_message(message, "user", save_to_db=True)
            self.message_input.delete(0, tk.END)
            # send over your connection
            self.conn.send(message)

    def poll_incoming(self):
        msg = self.conn.receive()
        if msg:
            self.add_message(msg, "peer", save_to_db=True)
        self.root.after(100, self.poll_incoming)
    def load_chat_history(self, ip_address):
        """Load chat history from database for a specific contact."""
        if not self.db:
            return
        
        # Get messages from database
        messages = self.db.get_messages(ip_address)
        
        if not messages:
            return
        
        # Clear current display
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)
        self.last_message_date = None
        self.chat_display.config(state="disabled")
        
        # Display each message from history
        for msg in messages:
            sender = "user" if msg.sender == "me" else "peer"
            # Load without saving again (save_to_db=False)
            self.add_message_with_timestamp(msg.message_text, sender, msg.timestamp, save_to_db=False)

    def add_message_with_timestamp(self, message, sender, timestamp, save_to_db=False):
        """Add a message with a specific timestamp (for loading history)."""
        self.chat_display.config(state="normal")

        time_str = timestamp.strftime("%I:%M %p").lstrip("0")
        date_str = timestamp.strftime("%B %d, %Y")

        # Date separator
        if date_str != self.last_message_date:
            if self.chat_display.index("end-1c") != "1.0":
                self.chat_display.insert(tk.END, "\n")
            self.chat_display.insert(tk.END, f"{date_str}\n", "date_separator")
            self.last_message_date = date_str

        if sender == "user":
            bubble_tag = "user_bubble"
            ts_tag = "timestamp_right"
            name = "You"
        else:
            bubble_tag = "peer_bubble"
            ts_tag = "timestamp_left"
            name = self.current_contact if self.current_contact else "Peer"

        # Display message
        self.chat_display.insert(tk.END, f"{name}\n", bubble_tag)
        self.chat_display.insert(tk.END, f"{message}\n", bubble_tag)
        self.chat_display.insert(tk.END, f"{time_str}\n", ts_tag)
        self.chat_display.insert(tk.END, "\n")

        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")
    
    def set_input_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.message_input.config(state=state)
        self.send_button.config(state=state)

        if enabled:
            self.message_input.config(bg="white")
            self.send_button.config(bg="#10b981")
        else:
            self.message_input.config(bg="#e5e7eb")
            self.send_button.config(bg="#6b7280")

    def update_connection_status(self, status):
        self.root.tile(f"CHat - {status}")

    def on_contact_select(self,event):
        selection = self.contact_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        self.current_contact = self.contacts[index]
        self.contact_name_label.config(text=self.current_contact)
        
        if self.db and self.peer_ip:
            self.load_chat_history(self.peer_ip)