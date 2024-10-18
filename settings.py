def select_language():
    print("Select Language:")
    print("1: English")
    print("2: Dutch")
    print("3: Chinese")
    language = input("Please select a language by entering the corresponding number: ")
    return language

def account_security():
    print("\nAccount Security:")
    print("1: Username")
    print("2: ID")
    print("3: Phone Number")
    print("4: Password")
    print("5: More Settings")
    choice = input("Select an option: ")
    
    if choice == "4":
        current_password = input("Please enter your current password: ")
        # Simulate password verification
        if current_password == "password123":  # Placeholder for actual password check
            new_password = input("Enter your new password: ")
            print("Password changed successfully!")
        else:
            print("Incorrect password. Try again.")
    else:
        print(f"You selected option {choice}")

def color_setting():
    print("\nColor Setting:")
    print("1: Black")
    print("2: White")
    color = input("Select a background color: ")
    if color == "1":
        print("Background set to Black.")
    elif color == "2":
        print("Background set to White.")
    else:
        print("Invalid selection.")

def sign_out():
    print("\nSign Out:")
    confirm = input("Are you sure you want to sign out? (1: Yes, 2: No): ")
    if confirm == "1":
        print("Signed out successfully.")
    else:
        print("Sign out canceled.")

def switch_account():
    print("\nSwitch Account:")
    new_username = input("Enter new username: ")
    new_password = input("Enter new password: ")
    print(f"Switched to account {new_username}.")

def company_info():
    print("\nCompany Info:")
    print("Company: Example Corp")
    print("Address: 1234 Innovation Drive")
    print("Email: contact@example.com")

def settings_system():
    while True:
        print("\nSettings Menu:")
        print("1: Select Language")
        print("2: Account Security")
        print("3: Color Setting")
        print("4: Sign Out")
        print("5: Switch Account")
        print("6: Company Info")
        print("0: Exit")

        choice = input("Please choose an option: ")

        if choice == "1":
            select_language()
        elif choice == "2":
            account_security()
        elif choice == "3":
            color_setting()
        elif choice == "4":
            sign_out()
        elif choice == "5":
            switch_account()
        elif choice == "6":
            company_info()
        elif choice == "0":
            print("Exiting settings system.")
            break
        else:
            print("Invalid option. Please try again.")

# Running the system
settings_system()
