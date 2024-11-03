from flask import Flask, render_template, request, redirect, url_for, flash
import os
import time  # Import the time module
from user_profile import (
    get_user,
    update_email,
    update_nickname,
    update_profile_picture,
    allowed_file,
    default_picture_filename
)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/profile_pictures')


@app.route('/')
def home():
    user = get_user()
    user_name = user.get('name', 'Guest')
    return render_template('index.html', active_page='home', user_name=user_name)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/newSpending')
def newSpending():
    return render_template('newSpending.html', active_page='newSpending')


@app.route('/savingGoal')
def savingGoal():
    return render_template('savingGoal.html', active_page='savingGoal')


@app.route('/setting')
def setting():
    return render_template('settings.html', active_page='setting')


@app.route('/userProfile', methods=['GET', 'POST'])
def userProfile():
    if request.method == 'POST':
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

    # For GET requests, render the template and pass the time module
    user = get_user()
    return render_template('userProfile.html', active_page='userProfile', user=user, time=time)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
