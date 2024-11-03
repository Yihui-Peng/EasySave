from flask import Flask, render_template, request
import os
import time  # Import the time module
from user_profile import (
    get_user, handle_user_profile_update
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
        # Delegate form processing to user_profile.py
        return handle_user_profile_update(request)

    # For GET requests, render the template and pass the time module
    user = get_user()
    return render_template('userProfile.html', active_page='userProfile', user=user, time=time)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
