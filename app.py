import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from database import db, Detail, User, Saving_Goal, Record
import datetime
from datetime import timedelta, datetime
import re
import time
from sqlalchemy import inspect
from import_database import initialize_database
from user_profile import get_user, update_email, update_nickname, update_profile_picture, allowed_file, default_picture_filename, handle_user_profile_update
from flask_migrate import Migrate
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from budget_allocation_algorithm import fetch_combined_financial_data, allocate_budget, generate_insights



app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/profile_pictures')


# #database connection
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
    user = User.query.filter_by(user_id = user_id).first()

    #Fetch the latest spending record
    spending = Record.query.filter_by(user_id = user.user_id).order_by(Record.date.desc()).first()

    #Fetch the latest saving goal
    savingGoal = Saving_Goal.query.filter_by(user_id = user.user_id).first()

    # Fetch combined financial data
    category_averages = fetch_combined_financial_data(user_id, db.session)

    # Get average disposable income and average spending
    avg_disposable_income = user.average_income or 0.0
    avg_spending = user.average_spending or 0.0

    # Determine savings goal
    if savingGoal:
        savings_goal = savingGoal.amount
    else:
        savings_goal = avg_disposable_income * 0.20  # Default to 20% if no goal set

    # Allocate budget
    allocations = allocate_budget(avg_disposable_income, savings_goal, category_averages)

    #Generate insights
    insights = generate_insights(allocations, category_averages)

    return render_template('index.html', active_page='home', user = user, prev_spending = spending, savingGoal = savingGoal, allocations = allocations, insights = insights)

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
        emailadress = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('register'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", emailadress):
            flash('Invalid email address.')
            return redirect(url_for('register'))
        
        existing_user = User.query.filter((User.username == username) | (User.emailadress == emailadress)).first()
        if existing_user:
            flash('Username or email already exists', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, emailadress=emailadress, password=password,
                        )
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
    if request.method == 'POST':
        amount = request.form.get('amount')
        category_level_1 = request.form.get('category-level-1')
        category_level_2 = request.form.get('category-level-2')
        date = request.form.get('date')
        note = request.form.get('note')
        user_id = session.get('user_id')


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

    return render_template('newRecords.html', active_page='newRecords')



# Import your models
from database import User, Detail, Saving_Goal, Record

def generate_normal_distribution_chart(filtered_data):
    # Extract the amount data
    amounts = filtered_data['amount']

    # Generate histogram and fit normal distribution curve
    plt.figure(figsize=(10, 6))
    count, bins, ignored = plt.hist(amounts, bins=15, density=True, alpha=0.6, color='b')

    # Fit normal distribution curve
    mean, std = np.mean(amounts), np.std(amounts)
    plt.plot(
        bins,
        1 / (std * np.sqrt(2 * np.pi)) * np.exp(-((bins - mean) ** 2) / (2 * std ** 2)),
        linewidth=2,
        color='r'
    )

    plt.xlabel('Spending Amount')
    plt.ylabel('Density')
    plt.title('Spending Distribution')
    plt.grid()
    plt.savefig('static/spending_distribution.png')
    plt.close()  # Close the figure

def generate_monthly_spending_chart(filtered_data):
    # Create a copy to avoid SettingWithCopyWarning
    filtered_data = filtered_data.copy()
    # Add a 'month' column
    filtered_data['month'] = pd.to_datetime(filtered_data['date']).dt.month
    monthly_data = filtered_data.groupby('month')['amount'].sum()

    # Generate bar chart
    plt.figure(figsize=(10, 6))
    monthly_data.plot(kind='bar', color='skyblue')
    plt.xlabel('Month')
    plt.ylabel('Total Spending')
    plt.title('Monthly Spending')
    plt.grid(axis='y')
    plt.savefig('static/monthly_spending.png')
    plt.close()  # Close the figure



@app.route('/details_and_charts', methods=['GET', 'POST'])
def details_and_charts():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    # 初始化选定的分类
    selected_category_level_1 = 'All Spending'
    selected_category_level_2 = 'All'

    if request.method == 'POST':
        # 获取用户选择的一级和二级分类
        selected_category_level_1 = request.form.get('category_level_1', 'All Spending')
        selected_category_level_2 = request.form.get('category_level_2', 'All')

        # 构建查询条件
        query = Record.query.filter_by(user_id=user_id)

        if selected_category_level_1 != 'All Spending':
            if selected_category_level_2 != 'All':
                # 过滤指定的一级和二级分类
                category_filter = f"{selected_category_level_1}:{selected_category_level_2}"
                query = query.filter(Record.category == category_filter)
            else:
                # 仅过滤一级分类，使用like匹配
                query = query.filter(Record.category.like(f"{selected_category_level_1}:%"))
        # 如果选择了“All Spending”，则不进行额外的过滤

        filtered_records = query.all()
    else:
        # 对于GET请求，获取当前用户的所有记录
        filtered_records = Record.query.filter_by(user_id=user_id).all()

    # 将记录转换为DataFrame
    data = []
    for record in filtered_records:
        data.append({
            'amount': record.amount,
            'date': record.date,
            'category': record.category,
        })
    filtered_data = pd.DataFrame(data)

    # 生成图表
    if not filtered_data.empty:
        generate_normal_distribution_chart(filtered_data)
        generate_monthly_spending_chart(filtered_data)
    else:
        # 如果没有数据，可选择显示提示或占位图表
        pass

    return render_template(
        'details_and_charts.html',
        records=filtered_records,
        selected_category_level_1=selected_category_level_1,
        selected_category_level_2=selected_category_level_2
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

        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

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
            start_datum=start_date,
            end_datum=end_date,
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
    goals = Saving_Goal.query.filter_by(user_id=user_id).all()  # Only fetch goals for the logged-in user

    return render_template('savingGoal.html', active_page='savingGoal', goals=goals)


@app.route('/delete_selected_goals', methods=['POST'])
def delete_selected_goals():
    if 'user_id' not in session:
        return render_template('login.html')

    goal_ids = request.form.getlist('goal_ids')

    if not goal_ids:
        flash("No goals selected for deletion.", "warning")
        return redirect(url_for('show_saving_goal_page'))

    # 将goal_ids转换为整数类型
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

            user.emailadress = new_email  # 注意字段名是 `emailadress`
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
    if 'user_id' not in session:
        return render_template('login.html')
    if request.method == 'POST':
        return handle_user_profile_update(request)
    user_id = session.get('user_id')
    user = get_user(user_id)
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

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)