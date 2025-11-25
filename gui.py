import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

class ChatGUI:
    def __init__(self, root, connection):
        self.root = root
        self.conn = connection
        self.root.title("Chat Interface")
        self.root.geometry("500x600")
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            root, 
            wrap=tk.WORD, 
            width=60, 
            height=25,
            state='disabled',
            font=("Arial", 10)
        )
        self.chat_display.pack(padx=10, pady=10)
        
        # Configure tags for styling
        self.chat_display.tag_config("user", foreground="#0066cc", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("bot", foreground="#009900", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("timestamp", foreground="#666666", font=("Arial", 8))
        
        # Input frame
        input_frame = tk.Frame(root)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        # Message input
        self.message_input = tk.Entry(input_frame, font=("Arial", 11))
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_input.bind("<Return>", self.send_message)
        
        # Send button
        self.send_button = tk.Button(
            input_frame, 
            text="Send", 
            command=self.send_message,
            bg="#0066cc",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        

        self.poll_incoming()
        
    def add_message(self, message, sender="user"):
        """Add a message to the chat display"""
        self.chat_display.config(state='normal')
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add sender name and message
        if sender == "user":
            self.chat_display.insert(tk.END, "You: ", "user")
        else:
            self.chat_display.insert(tk.END, "Peer: ", "peer")
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
    
    def send_message(self, event=None):
        """Handle sending a message"""
        message = self.message_input.get().strip()
        
        if message:
            # Display user message
            self.add_message(message, "user")
            
            # Clear input
            self.message_input.delete(0, tk.END)
            
            # Simulate bot response (replace with your logic)
    
    def poll_incoming(self):
        msg = self.conn.receive()
        if msg:
            self.add_message(msg, "peer")
        self.root.after(100, self.poll_incoming)