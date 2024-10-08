users = {}

def create_account():
    print("\n--- Create a New Account ---")
    username = input("Enter a username: ")
    if username in users:
        print("Username already exists. Please choose a different one.")
        return
    password = input("Enter a password: ")
    users[username] = password
    print(f"Account created successfully for {username}!\n")

def login():
    print("\n--- Log In ---")
    username = input("Enter your username: ")
    if username not in users:
        print("No account found with this username. Please create an account.")
        return
    password = input("Enter your password: ")
    if users[username] == password:
        print(f"Welcome back, {username}!")
    else:
        print("Incorrect password. Please try again.")

def main_menu():
    while True:
        print("\n--- Main Menu ---")
        print("1. Log In")
        print("2. Create a New Account")
        print("3. Exit")
        choice = input("Choose an option (1, 2, or 3): ")

        if choice == '1':
            login()
        elif choice == '2':
            create_account()
        elif choice == '3':
            print("Exiting the application. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()




import tkinter as tk
from tkinter import messagebox

# A dictionary to store user credentials (for now)
users = {}


# Function to handle account creation
def create_account():
    username = entry_username.get()
    password = entry_password.get()

    if username in users:
        messagebox.showerror("Error", "Username already exists. Please choose another.")
    elif not username or not password:
        messagebox.showerror("Error", "Please enter both a username and a password.")
    else:
        users[username] = password
        messagebox.showinfo("Success", f"Account created successfully for {username}!")
        entry_username.delete(0, tk.END)
        entry_password.delete(0, tk.END)


# Function to handle login
def login():
    username = entry_username.get()
    password = entry_password.get()

    if username not in users:
        messagebox.showerror("Error", "No account found. Please create an account.")
    elif users[username] != password:
        messagebox.showerror("Error", "Incorrect password. Please try again.")
    else:
        messagebox.showinfo("Welcome", f"Welcome back, {username}!")
        entry_username.delete(0, tk.END)
        entry_password.delete(0, tk.END)


# Main application window
root = tk.Tk()
root.title("Login System")

# Username and Password Labels and Entry fields
label_username = tk.Label(root, text="Username:")
label_username.grid(row=0, column=0, padx=10, pady=10)

entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1, padx=10, pady=10)

label_password = tk.Label(root, text="Password:")
label_password.grid(row=1, column=0, padx=10, pady=10)

entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1, padx=10, pady=10)

# Buttons for Login and Account Creation
button_login = tk.Button(root, text="Log In", command=login)
button_login.grid(row=2, column=0, padx=10, pady=10)

button_create = tk.Button(root, text="Create Account", command=create_account)
button_create.grid(row=2, column=1, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()

