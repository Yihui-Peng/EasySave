import os
from werkzeug.utils import secure_filename
from flask import current_app, flash, redirect, url_for
import time  # Import time for unique filenames

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


def get_user():
    """Retrieve the user data."""
    return user_data


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

        # Get the old filename to delete
        old_filename = user_data['profile_picture']
        if old_filename != default_picture_filename:
            old_filepath = os.path.join(upload_folder, old_filename)
            if os.path.exists(old_filepath):
                os.remove(old_filepath)

        # Update to the new filename
        user_data['profile_picture'] = unique_filename
        return True, unique_filename
    return False, None


def handle_user_profile_update(request):
    """Handle the user profile update logic based on the form type."""
    form_type = request.form.get('form_type')

    if form_type == 'upload_picture':
        # Upload profile picture
        file = request.files.get('profile_picture')
        if file and allowed_file(file.filename):
            success, filename = update_profile_picture(file)
            if success:
                flash('Upload success!', 'success')
            else:
                flash('Upload failed!', 'danger')
        else:
            flash('Upload a valid file!', 'warning')

    elif form_type == 'revert_picture':
        # Revert to Default Picture
        user = get_user()
        user['profile_picture'] = default_picture_filename
        flash('Profile picture has been reverted to the default.', 'info')

    elif form_type == 'update_profile':
        # Update user data
        name = request.form.get('name')
        email = request.form.get('email')
        nickname = request.form.get('nickname')

        user = get_user()
        if name:
            user['name'] = name
        if email:
            update_email(email)
        if nickname:
            update_nickname(nickname)

        flash('Profile information updated successfully!', 'success')

    # After handling POST, redirect to the same route to perform a GET request
    return redirect(url_for('userProfile'))
