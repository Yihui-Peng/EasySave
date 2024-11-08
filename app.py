from flask import Flask, render_template, request, redirect, url_for, flash
import os
import time
from sqlalchemy import inspect
from import_database import initialize_database
from database import db, StudentSpending, User, Saving_Goal, Records

# changed Spending to Records

import pandas as pd
from user_profile import get_user, update_email, update_nickname, update_profile_picture, allowed_file, default_picture_filename, handle_user_profile_update

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/profile_pictures')


# #database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


with app.app_context():
    # Check db file exists or not 
    if not os.path.exists(os.path.join('instance', 'data.db')):
        # create the db file and import database
        db.create_all()
        initialize_database()
        print("Database and data initialized.")
    else:
        #Check the table exists or not 
        if not StudentSpending.query.first():
            initialize_database()
            print("Data imported into existing database.")
        else:
            print("Database already initialized, no need to import CSV.")

@app.route('/data')
def get_data():
    with app.app_context():
        users = User.query.all()

    if not users:
        return "No data found in the database."

    result = []
    for user in users:
        user_info = f"Username: {user.username}, Email: {user.emailadress}, Gender: {user.gender}, Age: {user.age}, Year in School: {user.year_in_school}, Major: {user.major}"
        result.append(user_info)

        spendings = StudentSpending.query.filter_by(user_id=user.user_id).all()
        if spendings:
            for spending in spendings:
                spending_info = f" - Spending ID: {spending.spending_id}, Disposable Income: {spending.disposable_income}, Housing: {spending.housing}, Food: {spending.food}, Transportation: {spending.transportation}, Personal Care: {spending.personal_care}, Others: {spending.others}"
                result.append(spending_info)
        else:
            result.append(" - No spending records found.")

        saving_goals = Saving_Goal.query.filter_by(user_id=user.user_id).all()
        if saving_goals:
            for goal in saving_goals:
                goal_info = f" - Saving Goal ID: {goal.saving_goal_id}, Amount: {goal.amount}, Start Date: {goal.start_datum}, End Date: {goal.end_datum}, Progress: {goal.progress}, Progress Amount: {goal.progress_amount}"
                result.append(goal_info)
        else:
            result.append(" - No saving goals found.")

        spending_records = Spending.query.filter_by(user_id=user.user_id).all()
        if spending_records:
            for record in spending_records:
                record_info = f" - Spending Record ID: {record.spending}, Amount: {record.amount}, Date: {record.Datum}, Category: {record.Categorie}"
                result.append(record_info)
        else:
            result.append(" - No spending records found.")

        result.append("<hr>")

    return '<br>'.join(result)

@app.route('/')
def home():
    user = get_user()
    user_name = user.get('name', 'Guest')
    return render_template('index.html', active_page='home', user_name=user_name)

@app.route('/login')
def login():
    return render_template('login.html')


# Finished newRecords part
@app.route('/newRecords', methods=['GET', 'POST'])
def newSpending():
    if request.method == 'POST':
        amount = request.form.get('amount')
        category_level_1 = request.form.get('category-level-1')
        category_level_2 = request.form.get('category-level-2')
        date = request.form.get('date')
        note = request.form.get('note')

        if not amount or not category_level_1 or not category_level_2 or not date:
            flash('Please fill out all required fields', 'error')
            return redirect(url_for('newRecords'))

        new_record = Records(
            amount=float(amount),
            category_level_1=category_level_1,
            category_level_2=category_level_2,
            date=date,
            note=note
        )

        db.session.add(new_record)
        db.session.commit()

        flash('New record added successfully', 'success')
        return redirect(url_for('newRecords'))

    return render_template('newRecords.html', active_page='newRecords')


@app.route('/savingGoal')
def savingGoal():
    return render_template('savingGoal.html', active_page='savingGoal')


@app.route('/setting')
def setting():
    return render_template('settings.html', active_page='setting')

@app.route('/survey')
def suvery():
    return render_template('financial_survey_html_.html')

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