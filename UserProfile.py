import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

# Simulated user data
users = {
    'test_user': {
        'password': 'test123',
        'name': 'Test User',
        'profile_pic': None,
        'username': 'test_user',
        'phone_number': '123-456-7890',
        'email': 'test_user@example.com'
    }
}

class UserProfilePage:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.user_data = users[username]

        # Set up the profile frame
        self.profile_frame = tk.Frame(self.root)
        self.profile_frame.pack(pady=10)

        # Welcome message
        tk.Label(self.profile_frame, text=f"Welcome, {self.user_data['name']}").grid(row=0, column=0, pady=10)

        # Display profile picture (if available)
        self.profile_pic_label = tk.Label(self.profile_frame)
        self.load_profile_picture()  # Load or show placeholder image
        self.profile_pic_label.grid(row=1, column=0, pady=10)

        # Button to change profile picture
        tk.Button(self.profile_frame, text="Change Profile Picture", command=self.change_profile_pic).grid(row=2, column=0, pady=5)

        # Fields to change username, phone number, and email
        tk.Label(self.profile_frame, text="Change Username:").grid(row=3, column=0)
        self.username_entry = tk.Entry(self.profile_frame)
        self.username_entry.insert(0, self.user_data['username'])
        self.username_entry.grid(row=4, column=0, pady=5)

        tk.Label(self.profile_frame, text="Change Phone Number:").grid(row=5, column=0)
        self.phone_entry = tk.Entry(self.profile_frame)
        self.phone_entry.insert(0, self.user_data['phone_number'])
        self.phone_entry.grid(row=6, column=0, pady=5)

        tk.Label(self.profile_frame, text="Change Email:").grid(row=7, column=0)
        self.email_entry = tk.Entry(self.profile_frame)
        self.email_entry.insert(0, self.user_data['email'])
        self.email_entry.grid(row=8, column=0, pady=5)

        # Button to save changes
        tk.Button(self.profile_frame, text="Save Changes", command=self.save_profile_changes).grid(row=9, column=0, pady=10)

        # Button to log out
        tk.Button(self.profile_frame, text="Log Out", command=self.logout).grid(row=10, column=0, pady=10)

    def load_profile_picture(self):
        """Load the user's profile picture, or show a placeholder if none exists."""
        if self.user_data['profile_pic']:
            img = Image.open(self.user_data['profile_pic'])  # Open the image
            img = img.resize((100, 100), Image.Resampling.LANCZOS)  # Resize it to 100x100 pixels
            photo = ImageTk.PhotoImage(img)  # Convert to a format Tkinter can use
            self.profile_pic_label.config(image=photo)  # Set the label to show the picture
            self.profile_pic_label.image = photo  # Keep reference so the image doesn't disappear
        else:
            # Show text if no profile picture is set
            self.profile_pic_label.config(text="[No Profile Picture]")

    def change_profile_pic(self):
        """Open a dialog for the user to select a new profile picture."""
        file_path = filedialog.askopenfilename(title="Select Profile Picture", filetypes=[("Image files", "*.jpg *.png")])
        if file_path:
            # Update the user's profile picture with the selected file path
            self.user_data['profile_pic'] = file_path
            self.load_profile_picture()  # Reload the picture with the new one

    def save_profile_changes(self):
        """Save the changes to the profile information."""
        new_username = self.username_entry.get()
        new_phone = self.phone_entry.get()
        new_email = self.email_entry.get()

        if not new_username or not new_phone or not new_email:
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        # Ensure the new username isn't taken by another user
        if new_username != self.user_data['username'] and new_username in users:
            messagebox.showerror("Error", "Username already taken. Please choose another.")
            return

        # Save the new information
        self.user_data['username'] = new_username
        self.user_data['phone_number'] = new_phone
        self.user_data['email'] = new_email
        messagebox.showinfo("Success", "Profile updated successfully!")

    def logout(self):
        """Log out and close the profile window."""
        self.profile_frame.pack_forget()
        # Add any additional logic here for logging out


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = UserProfilePage(root, 'test_user')
    root.mainloop()
