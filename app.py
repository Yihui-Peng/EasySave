from flask import Flask, render_template
from user_profile import get_user, update_email, update_nickname, update_profile_picture

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/profile_pictures"

@app.route('/')
def home():
    return render_template('index.html', active_page='home')

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
    user = get_user()
    return render_template('userProfile.html', active_page='userProfile', user=user)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)