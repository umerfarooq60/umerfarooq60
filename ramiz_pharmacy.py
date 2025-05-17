import tkinter as tk

from tkinter import ttk, messagebox
import sqlite3

# --- Database Setup ---
conn = sqlite3.connect("ramiz_pharmacy.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    price REAL,
    quantity INTEGER
)
''')
conn.commit()

# --- Functions ---
def add_stock():
    name = entry_name.get().strip()
    try:
        price = float(entry_price.get())
        quantity = int(entry_quantity.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for price and quantity.")
        return

    if not name or price <= 0 or quantity <= 0:
        messagebox.showerror("Invalid Input", "Please enter valid medicine details.")
        return

    try:
        cursor.execute("INSERT INTO medicines (name, price, quantity) VALUES (?, ?, ?)", (name, price, quantity))
    except sqlite3.IntegrityError:
        cursor.execute("UPDATE medicines SET price = ?, quantity = quantity + ? WHERE name = ?", (price, quantity, name))
    conn.commit()
    update_stock_list()
    messagebox.showinfo("Success", "Medicine added/updated successfully.")

def update_stock_list():
    for row in stock_table.get_children():
        stock_table.delete(row)
    cursor.execute("SELECT * FROM medicines")
    for row in cursor.fetchall():
        stock_table.insert('', 'end', values=row)

def add_to_cart():
    selected = stock_table.focus()
    if not selected:
        return
    data = stock_table.item(selected, 'values')
    name = data[1]
    price = float(data[2])
    try:
        qty = int(entry_bill_qty.get())
        if qty <= 0 or qty > int(data[3]):
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Quantity", "Enter valid quantity.")
        return
    cart.append((name, price, qty))
    show_cart()

def show_cart():
    cart_box.delete(0, tk.END)
    for item in cart:
        name, price, qty = item
        cart_box.insert(tk.END, f"{name} x {qty} = ₹{price * qty:.2f}")

def generate_bill():
    if not cart:
        messagebox.showwarning("Empty Cart", "Add items to the cart first.")
        return
    total = 0
    for name, price, qty in cart:
        total += price * qty
        cursor.execute("UPDATE medicines SET quantity = quantity - ? WHERE name = ?", (qty, name))
    conn.commit()
    update_stock_list()
    messagebox.showinfo("Bill Generated", f"Total amount: ₹{total:.2f}")
    cart.clear()
    cart_box.delete(0, tk.END)

# --- GUI Setup ---
root = tk.Tk()
root.title("Ramiz Pharmacy Billing System")
root.geometry("850x650")
root.configure(bg="#d0e8f2")  # Light blue background

cart = []

# --- Styling ---
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
style.map("Treeview", background=[("selected", "#a3d2f2")])

# --- Frames ---
frame_top = tk.LabelFrame(root, text="Add New Stock", padx=10, pady=10, bg="#d0e8f2", font=("Arial", 10, "bold"))
frame_top.pack(fill="x", padx=10, pady=5)

tk.Label(frame_top, text="Name", bg="#d0e8f2").grid(row=0, column=0)
entry_name = tk.Entry(frame_top, bg="white")
entry_name.grid(row=0, column=1)

tk.Label(frame_top, text="Price", bg="#d0e8f2").grid(row=0, column=2)
entry_price = tk.Entry(frame_top, bg="white")
entry_price.grid(row=0, column=3)

tk.Label(frame_top, text="Quantity", bg="#d0e8f2").grid(row=0, column=4)
entry_quantity = tk.Entry(frame_top, bg="white")
entry_quantity.grid(row=0, column=5)

tk.Button(frame_top, text="Add / Update Stock", command=add_stock, bg="#72bcd4", fg="white").grid(row=0, column=6, padx=10)

# --- Stock Table ---
stock_table = ttk.Treeview(root, columns=("ID", "Name", "Price", "Qty"), show='headings', height=12)
stock_table.heading("ID", text="ID")
stock_table.heading("Name", text="Name")
stock_table.heading("Price", text="Price")
stock_table.heading("Qty", text="Quantity")
stock_table.pack(padx=10, pady=5, fill="x")
update_stock_list()

# --- Billing Frame ---
frame_bill = tk.LabelFrame(root, text="Billing", padx=10, pady=10, bg="#d0e8f2", font=("Arial", 10, "bold"))
frame_bill.pack(fill="x", padx=10, pady=5)

tk.Label(frame_bill, text="Quantity", bg="#d0e8f2").grid(row=0, column=0)
entry_bill_qty = tk.Entry(frame_bill, bg="white")
entry_bill_qty.grid(row=0, column=1)

tk.Button(frame_bill, text="Add to Bill", command=add_to_cart, bg="#72bcd4", fg="white").grid(row=0, column=2, padx=10)

cart_box = tk.Listbox(frame_bill, width=80, height=6, bg="white")
cart_box.grid(row=1, column=0, columnspan=3, pady=10)

tk.Button(frame_bill, text="Generate Bill", command=generate_bill, bg="#4a90e2", fg="white").grid(row=2, column=1)

root.mainloop()
