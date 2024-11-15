# user_profile.py

import os
from werkzeug.utils import secure_filename
from flask import current_app, flash, redirect, url_for
from database import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import time  # Import time for unique filenames

default_picture_filename = "default_picture.png"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user(user_id):
    """Retrieve the user from the database."""
    return User.query.filter_by(user_id=user_id).first()

def update_email(user, new_email):
    """Update the user's email."""
    user.emailadress = new_email
    db.session.commit()
    return True

def update_nickname(user, new_nickname):
    """Update the user's nickname."""
    user.nickname = new_nickname
    db.session.commit()
    return True

def update_profile_picture(user, file):
    """Save a new profile picture and update the user's profile picture data."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"  # Append timestamp to filename
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, unique_filename)

        # Save the file
        file.save(filepath)

        # Get the old filename to delete
        old_filename = user.profile_picture
        if old_filename != default_picture_filename:
            old_filepath = os.path.join(upload_folder, old_filename)
            if os.path.exists(old_filepath):
                os.remove(old_filepath)

        # Update to the new filename
        user.profile_picture = unique_filename
        db.session.commit()
        return True, unique_filename
    return False, None

def handle_user_profile_update(request):
    """Handle the user profile update logic based on the form type."""
    form_type = request.form.get('form_type')

    # Access user_id from session
    from flask import session
    user_id = session.get('user_id')
    if not user_id:
        flash("User not logged in.", "error")
        return redirect(url_for('login'))

    user = get_user(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('login'))

    if form_type == 'upload_picture':
        # Upload profile picture
        file = request.files.get('profile_picture')
        if file and allowed_file(file.filename):
            success, filename = update_profile_picture(user, file)
            if success:
                flash('Profile picture updated successfully!', 'success')
            else:
                flash('Failed to upload profile picture.', 'danger')
        else:
            flash('Please upload a valid image file.', 'warning')

    elif form_type == 'revert_picture':
        # Revert to Default Picture
        user.profile_picture = default_picture_filename
        db.session.commit()
        flash('Profile picture has been reverted to the default.', 'info')

    elif form_type == 'update_profile':
        # Update user data
        name = request.form.get('name')
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        average_income = request.form.get('average_income')
        average_spending = request.form.get('average_spending')
        age = request.form.get('age')
        gender = request.form.get('gender')
        year_in_school = request.form.get('year_in_school')
        major = request.form.get('major')

        if name:
            user.name = name
        if email:
            update_email(user, email)
        if nickname:
            update_nickname(user, nickname)
        if average_income:
            try:
                user.average_income = float(average_income)
            except ValueError:
                flash('Invalid input for average income.', 'warning')
        if average_spending:
            try:
                user.average_spending = float(average_spending)
            except ValueError:
                flash('Invalid input for average spending.', 'warning')
        if age:
            try:
                user.age = int(age)
            except ValueError:
                flash('Invalid input for age.', 'warning')
        if gender:
            user.gender = gender
        if year_in_school:
            user.year_in_school = year_in_school
        if major:
            user.major = major

        db.session.commit()
        flash('Profile information updated successfully!', 'success')

    # After handling POST, redirect to the same route to perform a GET request
    return redirect(url_for('userProfile'))
