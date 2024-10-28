# user_profile.py

import os
from werkzeug.utils import secure_filename

# Store only the filename
default_picture_filename = "default_picture.png"

user_data = {
    "name": "John Doe",
    "email": "jh@example.com",
    "nickname": "JH",
    "profile_picture": default_picture_filename
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/profile_pictures'

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
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Save the file
        file.save(filepath)
        user_data['profile_picture'] = filename  # Store only the filename
        return True, filename
    return False, None

def get_user():
    """Retrieve the user data."""
    return user_data
