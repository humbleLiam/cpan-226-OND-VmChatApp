import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime


class ChatGUI:
    def __init__(self, root, connection):
        self.root = root
        self.conn = connection
        self.root.title("Chat Interface")
        self.root.geometry("800x600")
        self.root.configure(bg="#1f2933")

        # Track current contact and last date for separators
        self.contacts = ["Support Bot", "Alice", "Bob", "Charlie"]
        self.contact_details = {
            "Support Bot": "support@example.com • Online",
            "Alice": "alice@example.com • Last seen 5 min ago",
            "Bob": "bob@example.com • Last seen yesterday",
            "Charlie": "charlie@example.com • Offline",
        }
        self.current_contact = self.contacts[0]
        self.last_message_date = None

        # Configure layout (sidebar + main area)
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

        for name in self.contacts:
            self.contact_listbox.insert(tk.END, name)

        # Select first contact by default
        self.contact_listbox.selection_set(0)
        #self.contact_listbox.bind("<<ListboxSelect>>", self.on_contact_select)

        # -------- Right: Main chat area --------
        main_area = tk.Frame(self.root, bg="#e5e7eb")
        main_area.grid(row=0, column=1, sticky="nsew")
        main_area.grid_rowconfigure(1, weight=1)
        main_area.grid_columnconfigure(0, weight=1)

        # Top contact info bar
        header = tk.Frame(main_area, bg="#111827", height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        self.contact_name_label = tk.Label(
            header,
            text=self.current_contact,
            bg="#111827",
            fg="white",
            font=("Arial", 12, "bold")
        )
        self.contact_name_label.pack(anchor="w", padx=15, pady=(10, 0))

        self.contact_info_label = tk.Label(
            header,
            text=self.contact_details.get(self.current_contact, ""),
            bg="#111827",
            fg="#9ca3af",
            font=("Arial", 9)
        )
        self.contact_info_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Chat display frame
        chat_frame = tk.Frame(main_area, bg="#e5e7eb")
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Chat display area (ScrolledText)
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

        # Configure tags for styling (bubbles, timestamps, separators)
        self.chat_display.tag_config(
            "user_bubble",
            background="#DCF8C6",
            lmargin1=150,  # indent from left (right-side bubble)
            lmargin2=150,
            rmargin=10,
            spacing1=5,
            spacing3=5
        )
        self.chat_display.tag_config(
            "bot_bubble",
            background="#FFFFFF",
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
        self.send_button.grid(row=1,column=1, padx=(5, 0))
        
    
        self.poll_incoming()
        
    def add_message(self, message, sender="user"):
        """Add a message to the chat display as a bubble with timestamp & date separators."""
        self.chat_display.config(state="normal")

        now = datetime.now()
        # 12-hour format, e.g. "2:51 PM"
        time_str = now.strftime("%I:%M %p").lstrip("0")
        date_str = now.strftime("%B %d, %Y")

        # Date separator (once per day)
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
            self.chat_display.insert(tk.END, "Peer: ", "peer")
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def send_message(self, event=None):
        """Handle sending a message."""
        message = self.message_input.get().strip()

        if message:
            # Display user message
            self.add_message(message, "user")

            # Clear input
            self.message_input.delete(0, tk.END)
            
            # Simulate bot response (replace with your logic)
            self.conn.send(message)
    
    def poll_incoming(self):
        msg = self.conn.receive()
        if msg:
            self.add_message(msg, "peer")
        self.root.after(100, self.poll_incoming)
