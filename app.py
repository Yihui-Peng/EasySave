from flask import Flask, render_template, request
import os
import time
from import_database import import_csv_to_db
from database import db, StudentSpending
import pandas as pd
from user_profile import get_user, update_email, update_nickname, update_profile_picture, allowed_file, default_picture_filename


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/profile_pictures')


# #database connection
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/git/repository/my-awesome-project/instance/data.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)
#
# if not os.path.exists("D:/git/repository/my-awesome-project/instance/data.db"):
#     with app.app_context():
#         db.create_all()  # 创建表
#         import_csv_to_db('student_spending.csv')
#         print("Database and data initialized.")

@app.route('/data')
def get_data():
    with app.app_context():
        data = StudentSpending.query.all()
    if not data:
        return "No data found in the database."
    return '<br>'.join([f"Age: {d.age}, Gender: {d.gender}, Year: {d.year_in_school}, Major: {d.major}, Monthly Income: {d.monthly_income}" for d in data])

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
        return handle_user_profile_update(request)

    user = get_user()
    return render_template('userProfile.html', active_page='userProfile', user=user, time=time)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



if __name__ == "__main__":
    app.run(debug=True)    