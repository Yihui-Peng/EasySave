from flask import Flask, render_template, request, redirect, url_for, flash
import os
import time
from sqlalchemy import inspect
from import_database import initialize_database
from database import db, Detail, User, Saving_Goal, Record  
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
        if not Detail.query.first():
            initialize_database()
            print("Data imported into existing database.")
        else:
            print("Database already initialized, no need to import CSV.")


# 11111 question: we should make the formatbetween newRecords and get_data the same, and make sure user_id been used in the same way
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

        spendings = Detail.query.filter_by(user_id=user.user_id).all()
        if spendings:
            for spending in spendings:
                income = spending.income if spending.income is not None else 0.0
                living_expense = spending.living_expense if spending.living_expense is not None else 0.0
                allowance = spending.allowance if spending.allowance is not None else 0.0
                disposable_income = income + living_expense + allowance
                spending_info = f" - Spending ID: {spending.detail_id}, Disposable Income: {disposable_income}, Housing: {spending.housing}, Food: {spending.food}, Transportation: {spending.transportation}, Personal Care: {spending.personal_care}, Others: {spending.others}"
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

        spending_records = Record.query.filter_by(user_id=user.user_id).all()
        if spending_records:
            for record in spending_records:
                record_info = f" - Spending Record ID: {record.record_id}, Amount: {record.amount}, Date: {record.datum}, Category: {record.categorie}"
                result.append(record_info)
        else:
            result.append(" - No spending records found.")

        result.append("<hr>")

    return '<br>'.join(result)

@app.route('/')
def home():
    user = User.query.filter_by(user_id = 1001).first()
    spending = Record.query.filter_by(user_id = user.user_id).order_by(Record.datum.desc()).first()
    savingGoal = Saving_Goal.query.filter_by(user_id = user.user_id).first()
    return render_template('index.html', active_page='home', user = user, prev_spending = spending, savingGoal = savingGoal)

@app.route('/login')
def login():
    return render_template('login.html')


# newRecords part
@app.route('/newRecords', methods=['GET', 'POST'])
def newRecords():
    if request.method == 'POST':
        amount = request.form.get('amount')
        category_level_1 = request.form.get('category-level-1')
        category_level_2 = request.form.get('category-level-2')
        date = request.form.get('date')
        note = request.form.get('note')


        # 11111 问题：将当前登录的用户的current_user_id使用为user_id，但前提是当前用户登录的current_user_id被正确储存，而且可以被这里调用。
        # 11111 Problem: Use the current_user_id of the currently logged in user as user_id, but only if the current user logged in current_user_id is stored correctly and can be called here.
        # if current_user.is_authenticated:
        #     user_id = current_user.id
        # else:
        #     flash('You must be logged in to create a new record.', 'error')
        #     return redirect(url_for('login'))
        user_id = 1001


        if not amount or not category_level_1 or not category_level_2 or not date:
            flash('Please fill out all required fields', 'error')
            return redirect(url_for('newRecords'))

        new_record = Record(
            amount=float(amount),
            category_level_1=category_level_1,
            category_level_2=category_level_2,
            date=date,
            note=note,
            user_id=user_id
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

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        user_id = 777  # For testing, we use user_id 777

        # Check if the skip checkbox is checked
        skip = request.form.get('skipFinancialRecords', None)

        if skip:
            # Save the first and third question's answers to the User table
            average_income = request.form.get('averageDisposableIncome', 0.0)
            average_spending = request.form.get('averageSpending', 0.0)

            user = User.query.filter_by(user_id=user_id).first()
            if user:
                user.average_income = average_income
                user.average_spending = average_spending
                db.session.commit()

            return "Survey data (average income and average spending) has been saved successfully."
        else:
            # Save the second question's answer to the Saving_Goal table
            saving_goal_amount = request.form.get('goalAmount', 0.0)
            current_date = datetime.now()
            start_datum = current_date
            end_datum = current_date + timedelta(days=30)
            saving_goal_id = f"{user_id}{current_date.strftime('%Y%m%d')}"

            new_saving_goal = Saving_Goal(
                saving_goal_id=saving_goal_id,
                user_id=user_id,
                amount=saving_goal_amount,
                start_datum=start_datum,
                end_datum=end_datum,
                progress="In Progress",
                progress_amount=0.0
            )
            db.session.add(new_saving_goal)

            # Save the monthly financial records to the Detail table
            current_month = datetime.now().month
            current_year = datetime.now().year
            months = []

            for i in range(1, 4):
                month = current_month - i
                year = current_year
                if month <= 0:
                    month += 12
                    year -= 1
                months.append((month, year))

            last_day_of_month = {
                1: "01.31", 2: "02.28", 3: "03.31", 4: "04.30", 5: "05.31", 6: "06.30",
                7: "07.31", 8: "08.31", 9: "09.30", 10: "10.31", 11: "11.30", 12: "12.31"
            }

            for month, year in months:
                month_name = datetime(year, month, 1).strftime('%B')
                detail_data = {
                    'user_id': user_id,
                    'datum': datetime.strptime(f"{year}-{month:02d}-{last_day_of_month[month].split('.')[1]}", "%Y-%m-%d")
                }
                for category in [
                    "income", "allowance", "living_expense", "tuition", "housing", "food",
                    "transportation", "study_materials", "entertainment", "personal_care",
                    "technology", "apparel", "travel", "others"
                ]:
                    amount = request.form.get(f'{month_name}_{category.capitalize()}', 0.0)
                    detail_data[category] = amount

                new_detail = Detail(**detail_data)
                db.session.add(new_detail)

            db.session.commit()

            return "Survey data (saving goal and spending details) have been saved successfully."

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