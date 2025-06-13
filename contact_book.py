import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkinter import font as tkfont

def initialize_database():
    """Initialize the SQLite database and create contacts table if it doesn't exist"""
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        address TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

class ContactBookApp:
    def __init__(self, root):
        """Initialize the main application window"""
        self.root = root
        self.root.title("Contact Book")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        
        self.title_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        self.label_font = tkfont.Font(family="Helvetica", size=12)
        self.button_font = tkfont.Font(family="Helvetica", size=10)
        
       
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        
        self.create_widgets()
        self.load_contacts()
    
    def create_widgets(self):
        """Create all the widgets for the main interface"""
       
        title_label = ttk.Label(
            self.main_frame,
            text="Contact Book",
            font=self.title_font
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
       
        search_frame = ttk.Frame(self.main_frame)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=40
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<KeyRelease>", self.search_contacts)
        
        search_button = ttk.Button(
            search_frame,
            text="Search",
            command=self.search_contacts
        )
        search_button.pack(side=tk.LEFT)
        
        
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=("Name", "Phone", "Email", "Address"),
            show="headings",
            selectmode="browse"
        )
        
        self.tree.grid(row=2, column=0, columnspan=2, sticky="nsew")
        
        
        self.tree.heading("Name", text="Name", anchor=tk.W)
        self.tree.heading("Phone", text="Phone", anchor=tk.W)
        self.tree.heading("Email", text="Email", anchor=tk.W)
        self.tree.heading("Address", text="Address", anchor=tk.W)
        
        self.tree.column("Name", width=150, stretch=tk.YES)
        self.tree.column("Phone", width=120, stretch=tk.YES)
        self.tree.column("Email", width=180, stretch=tk.YES)
        self.tree.column("Address", width=250, stretch=tk.YES)
        
        
        scrollbar = ttk.Scrollbar(
            self.main_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=2, column=2, sticky="ns")
        
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        
        add_button = ttk.Button(
            button_frame,
            text="Add Contact",
            command=self.show_add_contact_dialog
        )
        add_button.pack(side=tk.LEFT, padx=5)
        
        edit_button = ttk.Button(
            button_frame,
            text="Edit Contact",
            command=self.show_edit_contact_dialog
        )
        edit_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = ttk.Button(
            button_frame,
            text="Delete Contact",
            command=self.delete_contact
        )
        delete_button.pack(side=tk.LEFT, padx=5)
        
        
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)
    
    def load_contacts(self, search_query=None):
        """Load contacts from database into the treeview"""
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        
        if search_query:
            cursor.execute('''
                SELECT * FROM contacts 
                WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR address LIKE ?
                ORDER BY name
            ''', (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute('SELECT * FROM contacts ORDER BY name')
        
        rows = cursor.fetchall()
        conn.close()
        
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        
        for row in rows:
            self.tree.insert("", tk.END, values=(row[1], row[2], row[3], row[4]), iid=row[0])
    
    def add_contact(self, name, phone, email, address):
        """Add a new contact to the database"""
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contacts (name, phone, email, address)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, email, address))
        
        conn.commit()
        conn.close()
        self.load_contacts()
    
    def update_contact(self, contact_id, name, phone, email, address):
        """Update an existing contact in the database"""
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE contacts 
            SET name=?, phone=?, email=?, address=?
            WHERE id=?
        ''', (name, phone, email, address, contact_id))
        
        conn.commit()
        conn.close()
        self.load_contacts()
    
    def delete_contact(self):
        """Delete the selected contact from the database"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a contact to delete")
            return
        
        contact_id = selected_item[0]
        name = self.tree.item(contact_id, "values")[0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?"):
            conn = sqlite3.connect('contacts.db')
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM contacts WHERE id=?', (contact_id,))
            
            conn.commit()
            conn.close()
            self.load_contacts()
    
    def search_contacts(self, event=None):
        """Search contacts based on the search query"""
        search_query = self.search_var.get()
        self.load_contacts(search_query)
    
    def show_add_contact_dialog(self):
        """Show dialog for adding a new contact"""
        self.contact_dialog("Add New Contact", self.save_new_contact)
    
    def show_edit_contact_dialog(self):
        """Show dialog for editing an existing contact"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a contact to edit")
            return
        
        contact_id = selected_item[0]
        contact_data = self.tree.item(contact_id, "values")
        
        self.contact_dialog(
            "Edit Contact",
            lambda name, phone, email, address: self.save_edited_contact(
                contact_id, name, phone, email, address
            ),
            contact_data
        )
    
    def contact_dialog(self, title, save_command, contact_data=None):
        """Create a dialog window for adding/editing contacts"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.resizable(False, False)
        
        if contact_data:
            name, phone, email, address = contact_data
        else:
            name, phone, email, address = "", "", "", ""
        
        
        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.insert(0, name)
        
       
        ttk.Label(dialog, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        phone_entry = ttk.Entry(dialog, width=30)
        phone_entry.grid(row=1, column=1, padx=5, pady=5)
        phone_entry.insert(0, phone)
        
        
        ttk.Label(dialog, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.grid(row=2, column=1, padx=5, pady=5)
        email_entry.insert(0, email)
        
       
        ttk.Label(dialog, text="Address:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        address_entry = ttk.Entry(dialog, width=30)
        address_entry.grid(row=3, column=1, padx=5, pady=5)
        address_entry.insert(0, address)
        
       
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        save_button = ttk.Button(
            button_frame,
            text="Save",
            command=lambda: self.validate_and_save(
                save_command,
                name_entry.get(),
                phone_entry.get(),
                email_entry.get(),
                address_entry.get(),
                dialog
            )
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
       
        name_entry.focus_set()
        
        
        dialog.bind("<Return>", lambda e: save_button.invoke())
    
    def validate_and_save(self, save_command, name, phone, email, address, dialog):
        """Validate input and save the contact"""
        if not name or not phone:
            messagebox.showwarning("Warning", "Name and Phone are required fields")
            return
        
        save_command(name, phone, email, address)
        dialog.destroy()
    
    def save_new_contact(self, name, phone, email, address):
        """Save a new contact after validation"""
        self.add_contact(name, phone, email, address)
        messagebox.showinfo("Success", "Contact added successfully")
    
    def save_edited_contact(self, contact_id, name, phone, email, address):
        """Save an edited contact after validation"""
        self.update_contact(contact_id, name, phone, email, address)
        messagebox.showinfo("Success", "Contact updated successfully")


initialize_database()

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBookApp(root)
    root.mainloop()