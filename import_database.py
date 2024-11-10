from datetime import datetime
from flask import Flask
from database import db, Detail, User, Saving_Goal, Record
import pandas as pd


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def import_csv_to_db(csv_file):
    df = pd.read_csv(csv_file, header=0)

    with app.app_context():
        for index, row in df.iterrows():
            try:
                current_user_count = User.query.count()
                # 如果没有指定 username，那么自动生成一个
                default_username = f"user_{current_user_count + 1}"
                user_data = User(
                    username = default_username,
                    nickname = None,
                    emailadress = None,
                    password = None,
                    age=row.get('age', None),
                    gender=row.get('gender', 'Unknown'),
                    year_in_school=row.get('year_in_school', 'Unknown'),
                    major=row.get('major', 'Unknown'),
                )
                db.session.add(user_data)
                db.session.commit()

                studetnSpending_data = Detail(
                    user_id= user_data.user_id,
                    allowance = row.get('financial_aid', 0.0),
                    income =row.get('monthly_income', 0.0),
                    tuition=row.get('tuition', 0.0),
                    housing=row.get('housing', 0.0),
                    food=row.get('food', 0.0),
                    transportation=row.get('transportation', 0.0),
                    study_materials=row.get('books_supplies', 0.0),
                    entertainment=row.get('entertainment', 0.0),
                    personal_care=row.get('personal_care', 0.0) + row.get('health_wellness', 0.0),
                    technology=row.get('technology', 0.0),
                    others=row.get('miscellaneous', 0.0),
                    preferred_payment_method=row.get('preferred_payment_method', 'Unknown')
                )
                db.session.add(studetnSpending_data)
            except Exception as e:
                print(f"Error occurred while adding row {index}: {e}")

        db.session.commit()
        print("Data has been successfully imported.")

def generate_test_data():
    # Adding users
    user1 = User(username='test_user1', nickname='tester1', emailadress='test1@example.com', password='password1', age=20, gender='Male', year_in_school='Sophomore', major='Computer Science')
    user2 = User(username='test_user2', nickname='tester2', emailadress='test2@example.com', password='password2', age=22, gender='Female', year_in_school='Junior', major='Electrical Engineering')
    db.session.add_all([user1, user2])
    db.session.commit()

    # Adding student spending data
    spending1 = Detail(user_id=user1.user_id, living_expense = 800, allowance =70, income=500.0, tuition=2000.0, housing=800.0, food=300.0, transportation=100.0, study_materials=150.0, entertainment=50.0, personal_care=30.0, technology=120.0, others=60.0, preferred_payment_method='Credit Card')
    spending2 = Detail(user_id=user2.user_id, living_expense = 600, allowance =65, income=600.0, tuition=2500.0, housing=900.0, food=350.0, transportation=120.0, study_materials=180.0, entertainment=70.0, personal_care=40.0, technology=150.0, others=80.0, preferred_payment_method='Debit Card')
    db.session.add_all([spending1, spending2])
    db.session.commit()

    # Adding saving goals
    saving_goal1 = Saving_Goal(user_id=user1.user_id, amount=1000.0, start_datum=datetime(2024, 1, 1), end_datum=datetime(2024, 12, 31), progress='In Progress', progress_amount=300.0)
    saving_goal2 = Saving_Goal(user_id=user2.user_id, amount=2000.0, start_datum=datetime(2024, 2, 1), end_datum=datetime(2024, 10, 31), progress='In Progress', progress_amount=800.0)
    db.session.add_all([saving_goal1, saving_goal2])
    db.session.commit()

    # Adding spending records
    spending_record1 = Record(user_id=user1.user_id, amount=45.0, datum=datetime(2024, 4, 5), categorie='Studie_matrial', note='fundation books')
    spending_record2 = Record(user_id=user2.user_id, amount=60.0, datum=datetime(2024, 4, 7), categorie='Transport', note='charge-ov chipcard')
    spending_record3 = Record(user_id=user1.user_id, amount=150.0, datum=datetime(2024, 4, 10), categorie='Entertainment', note='KTV')
    db.session.add_all([spending_record1, spending_record2, spending_record3])
    db.session.commit() 
    
    print("Test data has been successfully generated.")


def initialize_database():
        db.create_all()
        import_csv_to_db('student_spending.csv')
        generate_test_data()

