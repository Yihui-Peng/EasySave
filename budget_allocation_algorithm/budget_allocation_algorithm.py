# This algorithm gives insights about how to spend money.
# These insights are printed on the home page.

from database import Detail, User
from sqlalchemy.orm import Session
from sqlalchemy import func

def fetch_combined_financial_data(user_id, db_session: Session):
    """
    Fetch and combine financial data for a specific user from the database.
    """
    # Fetch Detail records for the user
    db_records = db_session.query(
        Detail.income,
        Detail.allowance,
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
    ).filter(Detail.user_id == user_id).all()

    if not db_records:
        return {}

    # Calculate averages for each category
    category_sums = {
        'Income': 0.0,
        'Allowance': 0.0,
        'Living Expense': 0.0,
        'Tuition': 0.0,
        'Housing': 0.0,
        'Food': 0.0,
        'Transportation': 0.0,
        'Study Material': 0.0,
        'Entertainment': 0.0,
        'Personal Care': 0.0,
        'Technology': 0.0,
        'Apparel': 0.0,
        'Travel': 0.0,
        'Others': 0.0
    }

    for record in db_records:
        category_sums['Income'] += record.income or 0.0
        category_sums['Allowance'] += record.allowance or 0.0
        category_sums['Living Expense'] += record.living_expense or 0.0
        category_sums['Tuition'] += record.tuition or 0.0
        category_sums['Housing'] += record.housing or 0.0
        category_sums['Food'] += record.food or 0.0
        category_sums['Transportation'] += record.transportation or 0.0
        category_sums['Study Material'] += record.study_materials or 0.0
        category_sums['Entertainment'] += record.entertainment or 0.0
        category_sums['Personal Care'] += record.personal_care or 0.0
        category_sums['Technology'] += record.technology or 0.0
        category_sums['Apparel'] += record.apparel or 0.0
        category_sums['Travel'] += record.travel or 0.0
        category_sums['Others'] += record.others or 0.0

    num_records = len(db_records)
    category_averages = {category: (total / num_records) for category, total in category_sums.items()}

    # Fetch user's average disposable income and average spending from the User table
    user = db_session.query(User).filter(User.user_id == user_id).first()
    if user:
        category_averages['Disposable Income'] = user.average_income or 0.0
        category_averages['Average Spending'] = user.average_spending or 0.0
    else:
        category_averages['Disposable Income'] = 0.0
        category_averages['Average Spending'] = 0.0

    return category_averages

def allocate_budget(avg_disposable_income, savings_goal, category_averages):
    """
    Allocate the budget based on disposable income, savings goal, and average category spending.
    Implements the 50/30/20 rule as a base and adjusts based on user data.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Define budget percentages
    savings_percentage = 0.20
    needs_percentage = 0.50
    wants_percentage = 0.30

    logger.debug(f"Average Disposable Income: {avg_disposable_income}")
    logger.debug(f"Initial Savings Goal: {savings_goal}")

    # Adjust savings goal if it exceeds the default savings percentage
    default_savings = avg_disposable_income * savings_percentage
    if savings_goal < default_savings:
        savings_goal = default_savings
        logger.debug(f"Savings Goal adjusted to default savings: {savings_goal}")
    elif savings_goal > avg_disposable_income * 0.5:
        # Limit savings goal to a maximum of 50% of disposable income
        savings_goal = avg_disposable_income * 0.5
        logger.debug(f"Savings Goal limited to 50% of disposable income: {savings_goal}")

    budget_after_savings = avg_disposable_income - savings_goal
    logger.debug(f"Budget after Savings: {budget_after_savings}")

    # Calculate allocations based on 50/30/20 rule
    if (needs_percentage + wants_percentage) > 0:
        needs_budget = budget_after_savings * needs_percentage / (needs_percentage + wants_percentage)
        wants_budget = budget_after_savings * wants_percentage / (needs_percentage + wants_percentage)
    else:
        needs_budget = 0.0
        wants_budget = 0.0
        logger.warning("Needs and Wants percentages sum to zero. Allocating zero budget to needs and wants.")

    logger.debug(f"Needs Budget: {needs_budget}")
    logger.debug(f"Wants Budget: {wants_budget}")

    # Map categories to needs and wants
    needs_categories = ['Housing', 'Food', 'Transportation', 'Personal Care', 'Study Material', 'Tuition', 'Technology']
    wants_categories = ['Entertainment', 'Apparel', 'Travel', 'Others']

    allocations = {}

    # Allocate to needs
    total_needs = sum([category_averages.get(cat, 0.0) for cat in needs_categories])
    logger.debug(f"Total Needs Category Averages: {total_needs}")

    if total_needs > 0:
        for category in needs_categories:
            avg = category_averages.get(category, 0.0)
            ratio = avg / total_needs
            allocations[category] = needs_budget * ratio
            logger.debug(f"Allocating {allocations[category]} to {category} (Ratio: {ratio})")
    else:
        logger.warning("Total Needs Category Averages is zero. Allocating zero to needs categories.")
        for category in needs_categories:
            allocations[category] = 0.0

    # Allocate to wants
    total_wants = sum([category_averages.get(cat, 0.0) for cat in wants_categories])
    logger.debug(f"Total Wants Category Averages: {total_wants}")

    if total_wants > 0:
        for category in wants_categories:
            avg = category_averages.get(category, 0.0)
            ratio = avg / total_wants
            allocations[category] = wants_budget * ratio
            logger.debug(f"Allocating {allocations[category]} to {category} (Ratio: {ratio})")
    else:
        logger.warning("Total Wants Category Averages is zero. Allocating zero to wants categories.")
        for category in wants_categories:
            allocations[category] = 0.0

    # Include Savings
    allocations['Savings'] = savings_goal
    logger.debug(f"Allocating {savings_goal} to Savings")

    logger.debug(f"Final Allocations: {allocations}")
    return allocations

def generate_insights(allocations, category_averages):
    """
    Generate personalized insights based on budget allocations and spending patterns.
    """
    insights = []
    total_allocated = sum(allocations.values())

    print(f"[DEBUG] Total Allocated in Insights: {total_allocated}")

    if total_allocated == 0:
        insights.append("No budget allocations available to generate insights.")
        return insights

    # Example Insight 1: High spending categories
    high_spending_threshold = 0.15  # 15%
    for category, allocated in allocations.items():
        if category == 'Savings':
            continue
        proportion = allocated / total_allocated
        if proportion > high_spending_threshold:
            insights.append(f"Consider reviewing your spending on {category}, as it consumes a significant portion of your budget.")

    # Example Insight 2: Low savings
    if allocations.get('Savings', 0) < (sum(allocations.values()) * 0.20):
        insights.append("Your savings allocation is below the recommended 20%. Try to increase your savings to build a stronger financial foundation.")

    # Example Insight 3: Balanced Budget
    if not insights:
        insights.append("Great job! Your budget allocations follow recommended financial guidelines.")

    return insights