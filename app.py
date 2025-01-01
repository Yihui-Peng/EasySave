import os
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from database import db, Detail, User, Saving_Goal, Record
from datetime import timedelta, datetime
import re
import time
from sqlalchemy import func, inspect
from import_database import initialize_database
from user_profile import get_user, handle_user_profile_update
from flask_migrate import Migrate
import matplotlib.pyplot as plt
from budget_allocation_algorithm.budget_allocation_algorithm import fetch_combined_financial_data, allocate_budget, generate_insights
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import warnings
import pandas as pd
import numpy as np
import json


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/profile_pictures')

#database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)

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


# 11111 question: we should make the format between newRecords and get_data the same, and make sure user_id been used in the same way
@app.route('/data')
def get_data():
    with app.app_context():
        users = User.query.all()

    if not users:
        return "No data found in the database."

    result = []
    for user in users:
        user_info = f"Username: {user.username}, Email: {user.emailaddress}, Gender: {user.gender}, Age: {user.age}, Year in School: {user.year_in_school}, Major: {user.major}"
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
                goal_info = f" - Saving Goal ID: {goal.saving_goal_id}, Amount: {goal.amount}, Start Date: {goal.start_date}, End Date: {goal.end_date}, Progress: {goal.progress}, Progress Amount: {goal.progress_amount}"
                result.append(goal_info)
        else:
            result.append(" - No saving goals found.")

        spending_records = Record.query.filter_by(user_id=user.user_id).all()
        if spending_records:
            for record in spending_records:
                record_info = f" - Spending Record ID: {record.record_id}, Amount: {record.amount}, Date: {record.date}, Category: {record.category}"
                result.append(record_info)
        else:
            result.append(" - No spending records found.")

        result.append("<hr>")

    return '<br>'.join(result)

@app.route('/')
def loginPage():
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return render_template('login.html')

    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()

    #Fetch the latest spending record
    spending = Record.query.filter_by(user_id = user.user_id).order_by(Record.date.desc()).limit(3).all()
    # 查询今天的所有记录
    today = datetime.now().date()
    today_records = Record.query.filter(
        Record.user_id == user.user_id,
        func.date(Record.date) == today
    ).all()
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('login'))

    # Fetch the latest saving goal
    savingGoal = Saving_Goal.query.filter_by(user_id=user.user_id).order_by(Saving_Goal.end_date.desc()).first()


    savingGoals = Saving_Goal.query.filter_by(user_id = user.user_id).limit(3).all()
    achievedGoals = Saving_Goal.query.filter(
        Saving_Goal.user_id == user.user_id,
        Saving_Goal.progress == "finished"
        ).order_by(Saving_Goal.end_date.desc()).limit(3).all()
    print(achievedGoals)
    # Fetch combined financial datas
    category_averages = fetch_combined_financial_data(user_id, db.session)
    print(f"[DEBUG] Category Averages: {category_averages}")

    # Get average disposable income and average spending
    avg_disposable_income = user.average_income or 0.0
    avg_spending = user.average_spending or 0.0
    print(f"[DEBUG] Average Disposable Income: {avg_disposable_income}")
    print(f"[DEBUG] Average Spending: {avg_spending}")

    # Determine savings goal
    if savingGoal:
        savings_goal = savingGoal.amount
    else:
        savings_goal = avg_disposable_income * 0.20  # Default to 20% if no goal set

    # Allocate budget
    allocations = allocate_budget(avg_disposable_income, savings_goal, category_averages)

    # Generate insights
    insights = generate_insights(allocations, category_averages)

    # Calculate daily budget (sum of allocations excluding 'Savings')
    daily_budget = sum(amount for category, amount in allocations.items() if category != 'Savings')
    print(f"[DEBUG] Daily Budget: {daily_budget}")

    return render_template(
        'index.html',
        active_page='home',
        user=user,
        prev_spending=spending,
        savingGoals=savingGoals,
        allocations=allocations,
        insights=insights,
        daily_budget=round(daily_budget, 2),
        today_records = today_records, 
        achievedGoals = achievedGoals
    )
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.user_id
            return redirect(url_for('home'))
        else:
            flash('username or password is incorrect ', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        emailaddress = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('login.html', show_register=True)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", emailaddress):
            flash('Invalid email address.')
            return render_template('login.html', show_register=True)
        
        existing_user = User.query.filter((User.username == username) | (User.emailaddress == emailaddress)).first()
        if existing_user:
            flash('Username or email already exists', 'error')
            return render_template('login.html', show_register=True)
        
        new_user = User(username=username, emailaddress=emailaddress, password=password)
        db.session.add(new_user)
        db.session.commit()

        print(f"New user created with user_id: {new_user.user_id}")  # 添加调试输出
        session['user_id'] = new_user.user_id

        flash('Registration successful! Please complete this survey.')
        return redirect(url_for('survey'))
    return render_template('login.html')





# newRecords part
@app.route('/newRecords', methods=['GET', 'POST'])
def newRecords():
    if 'user_id' not in session:
        return render_template('login.html')
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id = user_id).first()
    if request.method == 'POST':
        amount = request.form.get('amount')
        category_level_1 = request.form.get('category-level-1')
        category_level_2 = request.form.get('category-level-2')
        date = request.form.get('date')
        note = request.form.get('note')


        if not amount or not category_level_1 or not category_level_2 or not date:
            flash('Please fill out all required fields', 'error')
            return redirect(url_for('newRecords'))

        # Make category level 1 and 2 to one categorie,  eg. Necessities: Housing
        category=f"{category_level_1}:{category_level_2}"

        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('newRecords'))

        new_record = Record(
            amount=round(float(amount),2),
            category=category,
            date=date_obj,
            note=note,
            user_id=user_id
            )

        db.session.add(new_record)
        db.session.commit()

        # flash('New record added successfully', 'success')
        # return redirect(url_for('newRecords'))
        return redirect(url_for('newRecords', added=True))

    return render_template('newRecords.html', active_page='newRecords', user=user)


def generate_and_forecast_spending_data(start_date, end_date, forecast_days=30):
    """
    Generate mock spending data and perform ARIMA forecasting for each category.

    Args:
        start_date (str): Start date for the data generation (e.g., '2023-01-01').
        end_date (str): End date for the data generation (e.g., '2023-12-31').
        forecast_days (int): Number of days to forecast. Defaults to 30.

    Returns:
        dict: Forecast results for each category.
    """
    # Suppress warnings for convergence issues
    warnings.filterwarnings("ignore", category=ConvergenceWarning)

    # Generate mock user spending data
    np.random.seed(42)
    months = pd.date_range(start=start_date, end=end_date, freq='M')
    data = {
        'datum': months,
        'Living_expense': np.random.randint(500, 1200, len(months)),
        'Allowance': np.random.randint(100, 300, len(months)),
        'Income': np.random.randint(800, 1500, len(months)),
        'Tuition': np.random.randint(3000, 5000, len(months)),
        'Housing': np.random.randint(400, 900, len(months)),
        'Food': np.random.randint(100, 400, len(months)),
        'Transportation': np.random.randint(50, 200, len(months)),
        'Study_material': np.random.randint(50, 300, len(months)),
        'Entertainment': np.random.randint(20, 150, len(months)),
        'Personal_care': np.random.randint(20, 100, len(months)),
        'Technology': np.random.randint(50, 300, len(months)),
        'Travel': np.random.randint(50, 400, len(months)),
        'Others': np.random.randint(20, 200, len(months))
    }
    df = pd.DataFrame(data)
    columns_to_sum = [
        'Living_expense', 'Allowance', 'Housing', 'Food', 'Transportation',
        'Study_material', 'Entertainment', 'Personal_care', 'Technology',
        'Travel', 'Others'
    ]
    existing_columns = [col for col in columns_to_sum if col in df.columns]
    df['Total_spending'] = df[existing_columns].sum(axis=1)

    # Set time index
    df['datum'] = pd.to_datetime(df['datum'])
    df.set_index('datum', inplace=True)

    # Forecast results dictionary
    forecast_results = {}

    # Perform ARIMA forecasting for each category
    for column in df.columns:
        if column != 'Total_spending':
            data_series = df[column]

            # Clean and preprocess data
            if data_series.isna().any():
                data_series = data_series.fillna(0)
            if not np.isfinite(data_series).all():
                data_series = data_series.replace([np.inf, -np.inf], 0)

            # Check for stationarity
            if adfuller(data_series)[1] > 0.05:
                data_series = data_series.diff().dropna()

            # Build ARIMA model with error handling
            try:
                model = ARIMA(data_series, order=(2, 1, 2))
                model_fit = model.fit()
            except np.linalg.LinAlgError:
                model = ARIMA(data_series, order=(1, 1, 1))
                model_fit = model.fit()

            # Forecast future data
            forecast = model_fit.get_forecast(steps=forecast_days)
            forecast_mean = forecast.predicted_mean.clip(lower=0)  # Ensure no negative values
            forecast_results[column] = forecast_mean

    return forecast_results

@app.route('/predict', methods=['GET'])
def predict():
    # Call the function to generate predictions
    forecast_results = generate_and_forecast_spending_data(start_date='2023-01-01', end_date='2023-12-31')

    # Calculate average prediction for the next month
    predictions = {category: values.mean() for category, values in forecast_results.items()}

    # Render the predictions on the HTML page
    return render_template('predict.html', predictions=predictions)



def get_monthly_spending_data(records):
    if not records:
        return {'labels': [], 'values': []}

    data = []
    for record in records:
        data.append({
            'amount': record.amount,
            'date': record.date
        })
    df = pd.DataFrame(data)

    if df.empty:
        return {'labels': [], 'values': []}

    df['month'] = pd.to_datetime(df['date']).dt.month
    monthly_data = df.groupby('month')['amount'].sum().reset_index()

    labels = monthly_data['month'].astype(str).tolist()
    values = monthly_data['amount'].tolist()

    return {'labels': labels, 'values': values}



@app.route('/details_and_charts', methods=['GET', 'POST'])
def details_and_charts():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()

    selected_category_level_1 = 'All Spending'
    selected_category_level_2 = 'All'
    user_records = []
    detail_amounts = []
    monthly_data = {'labels': [], 'values': []}

    category_mapping = {
        'Disposable_income': {
            'allowance': 'Allowance',
            'income': 'Income',
            'living_expense': 'Living Expense'
        },
        'Necessities': {
            'tuition': 'Tuition',
            'housing': 'Housing',
            'food': 'Food',
            'transportation': 'Transportation'
        },
        'Flexible_spending': {
            'study_materials': 'Study Materials',
            'entertainment': 'Entertainment',
            'technology': 'Technology',
            'personal_care': 'Personal Care'
        },
        'Others': {
            'apparel': 'Apparel',
            'travel': 'Travel',
            'others': 'Others'
        }
    }

    if request.method == 'POST':

        selected_category_level_1 = request.form.get('category_level_1', 'All Spending')
        selected_category_level_2 = request.form.get('category_level_2', 'All')


        user_records_query = Record.query.filter_by(user_id=user_id)

        if selected_category_level_2 != 'All':
            # 拼接分类名称（Category Level 1: Category Level 2）
            selected_category = f"{selected_category_level_1}:{selected_category_level_2}"
            user_records_query = user_records_query.filter(Record.category == selected_category)

        # 获取用户的消费记录，按照日期降序排序
        user_records = user_records_query.order_by(Record.date.desc()).all()

        # 获取所有用户的 Detail 数据
        all_details = Detail.query.all()

        # 从 Detail 中提取数据用于正态分布图
        detail_amounts = []
        for detail in all_details:
            if selected_category_level_2 != 'All':
                amount = getattr(detail, selected_category_level_2, 0.0)
                if amount and amount > 0:
                    detail_amounts.append(amount)
            else:
                # 如果选择了 "All"，累加一级分类下所有分类的金额
                total_amount = sum([
                    getattr(detail, field, 0.0)
                    for field in category_mapping.get(selected_category_level_1, {}).keys()
                ])
                if total_amount > 0:
                    detail_amounts.append(total_amount)


        # 获取月度消费数据
        monthly_data = get_monthly_spending_data(user_records)

    else:
        # 对于 GET 请求，可以保留初始化的空列表，或者根据需要提供初始数据
        pass  # detail_amounts 已在函数开头初始化为空列表

    # 序列化数据
    monthly_data_json = json.dumps(monthly_data)

    return render_template(
        'details_and_charts.html',
        user=user,
        records=user_records,
        selected_category_level_1=selected_category_level_1,
        selected_category_level_2=selected_category_level_2,
        category_mapping=category_mapping,
        monthly_data_json=monthly_data_json
    )



#Adding saving goals
@app.route('/savingGoal', methods=['GET', 'POST'])
def show_saving_goal_page():
    if 'user_id' not in session:
        return render_template('login.html')

    if request.method == 'POST':
        # Handle form submission
        amount = float(request.form.get('amount'))
        start_date_str = request.form.get('start-date')
        end_date_str = request.form.get('end-date')
        progress = request.form.get('progress')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        progress_amount_str = request.form.get('progress_amount')
        if progress_amount_str:
            progress_amount = float(progress_amount_str)
        else:
            progress_amount = amount  # If progress is 'finished', set progress_amount to the total amount

        user_id = session.get('user_id')

        # Save the new goal to the database
        new_goal = Saving_Goal(
            user_id=user_id,
            amount=amount,
            start_date=start_date,
            end_date=end_date,
            progress=progress,
            progress_amount=progress_amount
        )
        db.session.add(new_goal)
        db.session.commit()

        flash('Saving Goal added successfully!', 'success')

        # After saving, redirect to the same page to show updated goals list
        return redirect(url_for('show_saving_goal_page'))

    # If it's a GET request, fetch all the goals for the logged-in user
    user_id = session.get('user_id')
    user = User.query.filter_by(user_id = user_id).first()
    goals = Saving_Goal.query.filter_by(user_id=user_id).all()  # Only fetch goals for the logged-in user
    onGoingGoals = Saving_Goal.query.filter(
        Saving_Goal.user_id == user_id,
        Saving_Goal.progress == 'ongoing').order_by(Saving_Goal.end_date.desc()).limit(4).all()
    return render_template('savingGoal.html', active_page='savingGoal', user = user, goals=goals, onGoingGoals = onGoingGoals)


@app.route('/delete_selected_goals', methods=['POST'])
def delete_selected_goals():
    if 'user_id' not in session:
        return render_template('login.html')

    goal_ids = request.form.getlist('goal_ids')

    if not goal_ids:
        flash("No goals selected for deletion.", "warning")
        return redirect(url_for('show_saving_goal_page'))


    goal_ids = [int(goal_id) for goal_id in goal_ids if goal_id]

    if goal_ids:
        Saving_Goal.query.filter(Saving_Goal.saving_goal_id.in_(goal_ids)).delete(synchronize_session=False)
        db.session.commit()
        flash("Selected goals deleted successfully!", "success")
    else:
        flash("No valid goals to delete.", "warning")

    return redirect(url_for('show_saving_goal_page'))



@app.route('/setting')
def setting():
    user_id = session.get('user_id')

    if not user_id:
        flash("You must be logged in to access settings.", "error")
        return redirect(url_for('login'))

    user = User.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        data = request.get_json()
        action = data.get('action')

        # 修改密码
        if action == 'change_password':
            current_password = data.get('current_password')
            new_password = data.get('new_password')

            # 验证当前密码是否匹配（注意：需要移除 `check_password_hash`，直接比较明文密码）
            if not user or user.password != current_password:
                return jsonify(success=False, message="Incorrect current password."), 400

            # 存储明文新密码（不加密）
            user.password = new_password
            db.session.commit()
            return jsonify(success=True, message="Password updated successfully.")

        # 修改用户名
        elif action == 'change_username':
            new_username = data.get('new_username')
            if not new_username:
                return jsonify(success=False, message="Username cannot be empty."), 400

            # 检查用户名是否已存在
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                return jsonify(success=False, message="Username already taken."), 400

            user.username = new_username
            db.session.commit()
            return jsonify(success=True, message="Username updated successfully.")

        # 修改邮箱
        elif action == 'change_email':
            new_email = data.get('new_email')
            if not new_email or not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
                return jsonify(success=False, message="Invalid email address."), 400

            user.emailaddress = new_email 
            db.session.commit()
            return jsonify(success=True, message="Email updated successfully.")

        # 修改昵称
        elif action == 'change_nickname':
            new_nickname = data.get('new_nickname')
            if not new_nickname:
                return jsonify(success=False, message="Nickname cannot be empty."), 400

            user.nickname = new_nickname
            db.session.commit()
            return jsonify(success=True, message="Nickname updated successfully.")

    return render_template('settings.html', active_page='setting', user=user)

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    # 获取 user_id
    user_id = session.get('user_id')

    print(f"[DEBUG] Session user_id: {user_id}, type: {type(user_id)}")

    if not user_id:
        flash("Please log in to complete the survey.", "error")
        return redirect(url_for('login'))

    try:
        user_id = int(user_id)
    except ValueError:
        flash("Invalid user ID. Please log in again.", "error")
        return redirect(url_for('login'))

    # 获取用户对象
    user = User.query.filter_by(user_id=user_id).first()
    print(f"[DEBUG] User query result: {user}")

    if not user:
        print("[DEBUG] User not found in database.")
        flash("User not found. Please log in again.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # 获取第一个和第三个问题的答案
        average_income = request.form.get('averageDisposableIncome', 0.0)
        average_spending = request.form.get('averageSpending', 0.0)

        try:
            # 更新用户的平均收入和支出字段
            user.average_income = float(average_income)
            user.average_spending = float(average_spending)
            db.session.commit()
            print(f"[DEBUG] User data saved: Average Income = {average_income}, Average Spending = {average_spending}")
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] An error occurred while saving user data: {str(e)}")  # 调试输出
            flash(f"An error occurred while saving user data: {str(e)}", "error")
            return redirect(url_for('survey'))

        # 处理第二个问题：储蓄目标
        savings_goal_choice = request.form.get('savingsGoal', None)
        if savings_goal_choice == 'yes':
            saving_goal_amount = request.form.get('goalAmount', 0.0)
            if float(saving_goal_amount) > 0:
                try:
                    current_date = datetime.now()
                    start_date = current_date
                    end_date = current_date + timedelta(days=30)

                    print(f"[DEBUG] Attempting to save saving goal for user_id {user_id} with amount {saving_goal_amount}")

                    new_saving_goal = Saving_Goal(
                        user_id=user_id,
                        amount=float(saving_goal_amount),
                        start_date=start_date,
                        end_date=end_date,
                        progress=None,
                        progress_amount=None
                    )
                    db.session.add(new_saving_goal)
                    db.session.commit()
                    print("[DEBUG] Saving goal saved successfully.")
                except Exception as e:
                    db.session.rollback()
                    print(f"[ERROR] An error occurred while saving the saving goal: {str(e)}")  # 调试输出
                    flash(f"An error occurred while saving the saving goal: {str(e)}", "error")
                    return redirect(url_for('survey'))

        # 处理第四个问题：财务记录
        skip = request.form.get('skipFinancialRecords', None)
        print(f"[DEBUG] Skip financial records: {skip}")  # 调试输出

        if not skip:
            try:
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
                    1: "31", 2: "28", 3: "31", 4: "30", 5: "31", 6: "30",
                    7: "31", 8: "31", 9: "30", 10: "31", 11: "30", 12: "31"
                }

                for month, year in months:
                    month_name = datetime(year, month, 1).strftime('%B')
                    detail_data = {
                        'user_id': user_id,
                        'date': datetime.strptime(f"{year}-{month:02d}-{last_day_of_month[month]}", "%Y-%m-%d")
                    }
                    for category in [
                        "Income", "Allowance", "LivingExpense", "Tuition", "Housing", "Food",
                        "Transportation", "StudyMaterial", "Entertainment", "PersonalCare",
                        "Technology", "Apparel", "Travel", "Others"
                    ]:
                        amount = request.form.get(f'{month_name}_{category}', 0.0)
                        if amount == '':
                            amount = 0.0
                        detail_data[category.lower()] = float(amount)
                        print(f"[DEBUG] Retrieved amount for {month_name}_{category}: {amount}")  # 调试输出

                    # 创建新的 Detail 实例并保存
                    new_detail = Detail(**detail_data)
                    db.session.add(new_detail)

                db.session.commit()
                print("[DEBUG] Financial records saved successfully.")
            except Exception as e:
                db.session.rollback()
                print(f"[ERROR] An error occurred while saving financial records: {str(e)}")  # 调试输出
                flash(f"An error occurred while saving financial records: {str(e)}", "error")
                return redirect(url_for('survey'))
        else:
            print("[DEBUG] User chose to skip financial records.")

        # 在所有数据处理后，显示感谢消息并重定向至主页
        flash("Thank you for completing the survey!", "success")
        return redirect(url_for('home'))

    return render_template('financial_survey_html_.html')

@app.route('/userProfile', methods=['GET', 'POST'])
def userProfile():
    user_id = session.get('user_id')
    user = get_user(user_id)
    if 'user_id' not in session:
        return render_template('login.html')
    if request.method == 'POST':
        return handle_user_profile_update(request, user_id)
    
    return render_template('userProfile.html', active_page='userProfile', user=user, time=time)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/budget', methods=['GET', 'POST'])
def budget_allocation():
    if 'user_id' not in session:
        flash("Please log in to view your budget allocation.", "error")
        return redirect(url_for('login'))

    user_id = int(session.get('user_id'))

    if request.method == 'POST':
        try:
            # Fetch combined financial data from the database
            category_averages = fetch_combined_financial_data(user_id, db.session)

            # Fetch user's average disposable income and average spending from the User table
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return jsonify({"error": "User not found."}), 404

            avg_disposable_income = user.average_income or 0.0
            avg_spending = user.average_spending or 0.0

            # Fetch or set savings goal
            saving_goal_record = Saving_Goal.query.filter_by(user_id=user_id).order_by(Saving_Goal.end_date.desc()).first()
            if saving_goal_record:
                savings_goal = saving_goal_record.amount
            else:
                savings_goal = avg_disposable_income * 0.20  # Default to 20% if no goal set

            # Perform budget allocation
            allocations = allocate_budget(avg_disposable_income, savings_goal, category_averages)

            # Generate insights
            insights = generate_insights(allocations, category_averages)

            # Prepare the response data
            response_data = {
                "Disposable Income": round(avg_disposable_income, 2),
                "Savings Goal": round(allocations.get('Savings', 0.0), 2),
                "Budget After Savings": round(avg_disposable_income - allocations.get('Savings', 0.0), 2),
                "Allocations": {category: round(amount, 2) for category, amount in allocations.items()},
                "Insights": insights
            }

            return jsonify(response_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # For GET request, render a simple form or page
    return render_template('budget.html')

@app.route('/logout')
def logout():
    session['user_id'] = None
    return redirect(url_for('login'))


#Needed for profile picture
@app.context_processor
def inject_time():
    import time
    return dict(time=time)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
