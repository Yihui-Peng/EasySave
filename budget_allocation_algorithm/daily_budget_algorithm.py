from database import Detail, User, Saving_Goal
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def fetch_user_financial_data(user_id, db_session: Session):
    """
    Fetch user's financial data, including income, expenses, and saving goals.
    """
    # Fetch the latest Detail record for the user
    latest_detail = db_session.query(Detail).filter(Detail.user_id == user_id).order_by(Detail.date.desc()).first()

    if not latest_detail:
        return None

    # Fetch user's active saving goals (excluding finished ones)
    saving_goals = db_session.query(Saving_Goal).filter(
        Saving_Goal.user_id == user_id,
        Saving_Goal.progress != 'finished'
    ).all()

    # Calculate total income (income + allowance + living_expense)
    total_income = sum([
        latest_detail.income or 0,
        latest_detail.allowance or 0,
        latest_detail.living_expense or 0
    ])

    # Calculate total fixed expenses (e.g., tuition, housing)
    fixed_expenses = sum([
        latest_detail.tuition or 0,
        latest_detail.housing or 0
    ])

    # Calculate total variable expenses (other categories)
    variable_expenses = sum([
        latest_detail.food or 0,
        latest_detail.transportation or 0,
        latest_detail.study_materials or 0,
        latest_detail.entertainment or 0,
        latest_detail.personal_care or 0,
        latest_detail.technology or 0,
        latest_detail.apparel or 0,
        latest_detail.travel or 0,
        latest_detail.others or 0
    ])

    return {
        'total_income': total_income,
        'fixed_expenses': fixed_expenses,
        'variable_expenses': variable_expenses,
        'saving_goals': saving_goals
    }

def calculate_daily_savings(saving_goals):
    """
    Calculate the total daily savings required to meet all saving goals by their end dates.
    Prioritize saving goals to maximize the chances to reach all goals.
    """
    today = datetime.now().date()
    daily_savings = 0.0

    # Prioritize goals by earliest end date
    prioritized_goals = sorted(saving_goals, key=lambda x: x.end_date)

    for goal in prioritized_goals:
        remaining_amount = (goal.amount or 0) - (goal.progress_amount or 0)
        days_left = (goal.end_date.date() - today).days

        if days_left <= 0 or remaining_amount <= 0:
            continue  # Skip goals that are already completed or past their end date

        daily_saving_for_goal = remaining_amount / days_left
        daily_savings += daily_saving_for_goal

    return daily_savings

def calculate_daily_budget(user_financial_data):
    """
    Calculate the daily budget based on income, expenses, and saving goals.
    """
    total_income = user_financial_data['total_income']
    fixed_expenses = user_financial_data['fixed_expenses']
    variable_expenses = user_financial_data['variable_expenses']
    saving_goals = user_financial_data['saving_goals']

    # Get the number of days left in the current month
    today = datetime.now().date()
    current_year = today.year
    current_month = today.month
    days_in_month = (datetime(current_year, current_month % 12 + 1, 1) - timedelta(days=1)).day
    days_left_in_month = days_in_month - today.day + 1

    # Calculate the available income after fixed expenses
    available_income = total_income - fixed_expenses

    if not saving_goals:
        # No saving goals; distribute available income over the remaining days
        daily_budget = available_income / days_left_in_month
        return max(daily_budget, 0.0)

    # Calculate required daily savings to meet saving goals
    daily_savings = calculate_daily_savings(saving_goals)

    # Calculate the daily budget
    total_variable_budget = available_income - (daily_savings * days_left_in_month)
    daily_budget = total_variable_budget / days_left_in_month

    return max(daily_budget, 0.0)

def generate_daily_budget(user_id, db_session: Session):
    user_financial_data = fetch_user_financial_data(user_id, db_session)
    if not user_financial_data:
        raise ValueError("Insufficient financial data for user.")

    daily_budget = calculate_daily_budget(user_financial_data)
    return round(daily_budget, 2)

