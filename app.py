from flask import Flask, render_template, request, redirect, url_for, flash
import os
from user_profile import get_user, update_email, update_nickname, update_profile_picture, allowed_file, default_picture_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = "static/profile_pictures"

@app.route('/')
def home():
    user = get_user()
    user_name = user.get('name','Guest')
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

@app.route('/userProfile', methods = ['GET', 'POST'])
def userProfile():
    if request.method == 'POST':
        #Upload profile picture
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                success, filename = update_profile_picture(file)
                if success:
                    flash('Upload success!','success')
                else:
                    flash('Upload failed!','danger')
            else:
                flash('Upload a valid file!','warning')

        # Revert to Default Picture
        elif 'revert_picture' in request.form:
            get_user()['profile_picture'] = default_picture_filename
            flash('Profile picture has been reverted to the default.', 'info')

        name = request.form.get('name')
        email = request.form.get('email')
        nickname = request.form.get('nickname')

        # Update user data
        if name:
            get_user()['name'] = name
        if email:
            update_email(email)
        if nickname:
            update_nickname(nickname)

        flash('Profile information updated successfully!', 'success')

    user = get_user()
    return render_template('userProfile.html', active_page='userProfile', user=user)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)