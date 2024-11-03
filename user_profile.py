import os
from werkzeug.utils import secure_filename
from flask import current_app
import time  # Import time for unique filenames

# Store only the filename
default_picture_filename = "default_picture.png"

user_data = {
    "name": "John Doe",
    "email": "jh@example.com",
    "nickname": "JH",
    "profile_picture": default_picture_filename
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_email(new_email):
    """Update the user's email."""
    user_data['email'] = new_email
    return True

def update_nickname(new_nickname):
    """Update the user's nickname."""
    user_data['nickname'] = new_nickname
    return True

def update_profile_picture(file):
    """Save a new profile picture and update the user's profile picture data."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"  # Append timestamp to filename
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, unique_filename)

        # Save the file
        file.save(filepath)
        user_data['profile_picture'] = unique_filename  # Store the unique filename
        return True, unique_filename
    return False, None

def get_user():
    """Retrieve the user data."""
    return user_data
