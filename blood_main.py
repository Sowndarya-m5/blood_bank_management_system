import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
from datetime import date

# ---------------- MySQL Connection ---------------- #
db = mysql.connector.connect(
    host="localhost",
    user="root",      # change to your MySQL username
    password="Sownd@05",      # change to your MySQL password
    database="blood_bank_db"
)
cursor = db.cursor()

# ---------------- Create Tables ---------------- #
cursor.execute("""
CREATE TABLE IF NOT EXISTS donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    gender VARCHAR(10),
    phone VARCHAR(15),
    age INT,
    weight INT,
    blood_group VARCHAR(5),
    packets INT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    phone VARCHAR(15),
    blood_group VARCHAR(5),
    packets INT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS hospital_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_name VARCHAR(50),
    blood_group VARCHAR(5),
    packets INT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS blood_inventory (
    blood_group VARCHAR(5) PRIMARY KEY,
    quantity INT
)
""")

# Initialize inventory if empty
blood_types = ["A+", "O+", "B+", "AB+", "A-", "O-", "B-", "AB-"]
cursor.execute("SELECT COUNT(*) FROM blood_inventory")
if cursor.fetchone()[0] == 0:
    for b in blood_types:
        cursor.execute("INSERT INTO blood_inventory (blood_group, quantity) VALUES (%s, %s)", (b, 10))
    db.commit()

# ---------------- Tkinter GUI ---------------- #
root = tk.Tk()
root.title("Blood Bank Management System")
root.geometry("600x400")

# ---------------- Inventory Display ---------------- #
def show_inventory():
    cursor.execute("SELECT * FROM blood_inventory")
    data = cursor.fetchall()
    inventory_text = "Available Blood Packets:\n"
    for b, q in data:
        inventory_text += f"{b}: {q} packets\n"
    messagebox.showinfo("Blood Inventory", inventory_text)

# ---------------- Donor Registration ---------------- #
def donor_registration():
    name = simpledialog.askstring("Donor", "Enter Name:")
    gender = simpledialog.askstring("Donor", "Enter Gender (M/F):")
    phone = simpledialog.askstring("Donor", "Enter Phone Number:")
    age = int(simpledialog.askstring("Donor", "Enter Age:"))
    weight = int(simpledialog.askstring("Donor", "Enter Weight (kg):"))
    blood_group = simpledialog.askstring("Donor", "Enter Blood Group (A+, O+, B+, AB+, A-, O-, B-, AB-):")
    packets = int(simpledialog.askstring("Donor", "Enter Packets (1 packet = 200ml):"))

    # Update inventory
    cursor.execute("SELECT quantity FROM blood_inventory WHERE blood_group=%s", (blood_group,))
    current_qty = cursor.fetchone()[0]
    cursor.execute("UPDATE blood_inventory SET quantity=%s WHERE blood_group=%s", (current_qty + packets, blood_group))
    db.commit()

    # Insert donor info
    cursor.execute("INSERT INTO donors (name, gender, phone, age, weight, blood_group, packets) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                   (name, gender, phone, age, weight, blood_group, packets))
    db.commit()

    # Receipt
    messagebox.showinfo("Donor Receipt",
                        f"Name: {name}\nPhone: {phone}\nBlood Group: {blood_group}\nPackets Donated: {packets}\nThank you for donating!")

# ---------------- Patient Blood Request ---------------- #
def patient_request():
    name = simpledialog.askstring("Patient", "Enter Your Name:")
    phone = simpledialog.askstring("Patient", "Enter Your Phone Number:")
    blood_group = simpledialog.askstring("Patient", "Enter Required Blood Group (A+, O+, B+, AB+, A-, O-, B-, AB-):")
    packets = int(simpledialog.askstring("Patient", "Enter Number of Packets (1 packet = 200ml):"))

    # Check availability
    cursor.execute("SELECT quantity FROM blood_inventory WHERE blood_group=%s", (blood_group,))
    qty = cursor.fetchone()[0]

    if qty >= packets:
        cursor.execute("UPDATE blood_inventory SET quantity=%s WHERE blood_group=%s", (qty - packets, blood_group))
        db.commit()

        # Insert patient info
        cursor.execute("INSERT INTO patients (name, phone, blood_group, packets) VALUES (%s,%s,%s,%s)",
                       (name, phone, blood_group, packets))
        db.commit()

        messagebox.showinfo("Patient Receipt",
                            f"Name: {name}\nPhone: {phone}\nBlood Group: {blood_group}\nPackets Received: {packets}")
    else:
        messagebox.showwarning("Unavailable", f"Only {qty} packets of {blood_group} available!")

# ---------------- Hospital Blood Request ---------------- #
def hospital_request():
    hospitals = {
        "Sugam": "sug01",
        "KS": "ks02",
        "Anbu": "anb03",
        "GH": "gh04",
        "N.M": "nm05"
    }

    hospital_name = simpledialog.askstring("Hospital", "Enter Hospital Name:")
    password = simpledialog.askstring("Hospital", "Enter Password:")

    if hospital_name in hospitals and hospitals[hospital_name] == password:
        blood_group = simpledialog.askstring("Hospital", "Enter Blood Group Needed (A+, O+, B+, AB+, A-, O-, B-, AB-):")
        packets = int(simpledialog.askstring("Hospital", "Enter Number of Packets (1 packet = 200ml):"))

        cursor.execute("SELECT quantity FROM blood_inventory WHERE blood_group=%s", (blood_group,))
        qty = cursor.fetchone()[0]

        if qty >= packets:
            cursor.execute("UPDATE blood_inventory SET quantity=%s WHERE blood_group=%s", (qty - packets, blood_group))
            db.commit()

            # Insert hospital request
            cursor.execute("INSERT INTO hospital_requests (hospital_name, blood_group, packets) VALUES (%s,%s,%s)",
                           (hospital_name, blood_group, packets))
            db.commit()

            messagebox.showinfo("Hospital Receipt",
                                f"Hospital: {hospital_name}\nBlood Group: {blood_group}\nPackets Received: {packets}")
        else:
            messagebox.showwarning("Unavailable", f"Only {qty} packets of {blood_group} available!")
    else:
        messagebox.showerror("Error", "Invalid Hospital Name or Password!")

# ---------------- Admin Login ---------------- #
def admin_login():
    admin_user = simpledialog.askstring("Admin Login", "Enter Admin Username:")
    admin_pass = simpledialog.askstring("Admin Login", "Enter Admin Password:")
    if admin_user == "muruga20" and admin_pass == "muruga20":
        main_menu()
    else:
        messagebox.showerror("Error", "Unauthorized Access!")

# ---------------- Main Menu ---------------- #
def main_menu():
    menu_window = tk.Toplevel(root)
    menu_window.title("Blood Bank Menu")
    menu_window.geometry("400x300")

    tk.Button(menu_window, text="1. Donor Registration", width=30, command=donor_registration).pack(pady=10)
    tk.Button(menu_window, text="2. Patient Blood Request", width=30, command=patient_request).pack(pady=10)
    tk.Button(menu_window, text="3. Hospital Blood Request", width=30, command=hospital_request).pack(pady=10)
    tk.Button(menu_window, text="4. Available Blood Packets", width=30, command=show_inventory).pack(pady=10)
    tk.Button(menu_window, text="5. Exit", width=30, command=menu_window.destroy).pack(pady=10)

# ---------------- Main App ---------------- #
tk.Button(root, text="Admin Login", width=20, height=2, command=admin_login).pack(pady=100)
root.mainloop()
