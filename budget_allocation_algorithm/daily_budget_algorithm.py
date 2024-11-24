#This algorithm calculates the daily budget the user should spend.
#The number calculated is printed on the home page.

from database import Detail, User
from sqlalchemy.orm import Session

def fetch_user_financial_data(user_id, db_session: Session):
    """
    Fetch historical spending data and user financial information.
    """
    # Fetch Detail records for the user
    db_records = db_session.query(
        Detail.date,
        Detail.living_expense,
        Detail.tuition,
        Detail.housing,
        Detail.food,
        Detail.transportation,
        Detail.study_materials,
        Detail.entertainment,
        Detail.personal_care,
        Detail.technology,
        Detail.apparel,
        Detail.travel,
        Detail.others
    ).filter(Detail.user_id == user_id).order_by(Detail.date.desc()).all()

    if not db_records:
        return None

    # Fetch user's saving goal and time frame from User table
    user = db_session.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None

    return {
        'records': db_records,
        'saving_goal': user.saving_goal,
        'time_frame_days': user.time_frame_days
    }

def calculate_average_daily_spending(records):
    """
    Calculate the average daily spending based on historical records.
    """
    total_spent = 0.0
    total_days = 0

    for record in records:
        daily_total = (
            (record.living_expense or 0) +
            (record.tuition or 0) +
            (record.housing or 0) +
            (record.food or 0) +
            (record.transportation or 0) +
            (record.study_materials or 0) +
            (record.entertainment or 0) +
            (record.personal_care or 0) +
            (record.technology or 0) +
            (record.apparel or 0) +
            (record.travel or 0) +
            (record.others or 0)
        )
        total_spent += daily_total
        total_days += 1

    if total_days == 0:
        return 0.0

    average_daily_spending = total_spent / total_days
    return average_daily_spending

def allocate_daily_budget(user_financial_data):
    """
    Allocate a daily budget to help the user reach their savings goal.
    """
    saving_goal = user_financial_data['saving_goal']
    time_frame_days = user_financial_data['time_frame_days']
    records = user_financial_data['records']

    average_daily_spending = calculate_average_daily_spending(records)

    # Calculate required daily savings
    required_daily_savings = saving_goal / time_frame_days

    # Determine allocatable daily budget
    allocatable_daily_budget = average_daily_spending - required_daily_savings

    # Ensure the budget is not negative
    if allocatable_daily_budget < 0:
        allocatable_daily_budget = 0.0  # Or handle as needed

    return {
        'average_daily_spending': round(average_daily_spending, 2),
        'required_daily_savings': round(required_daily_savings, 2),
        'allocatable_daily_budget': round(allocatable_daily_budget, 2)
    }

def generate_daily_budget(user_id, db_session: Session):
    """
    Main function to generate daily budget for a user to reach their savings goal.
    """
    user_financial_data = fetch_user_financial_data(user_id, db_session)
    if not user_financial_data:
        raise ValueError("Insufficient financial data for user.")

    budget_allocation = allocate_daily_budget(user_financial_data)
    return budget_allocation