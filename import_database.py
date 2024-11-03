from flask import Flask
from database import db, StudentSpending
import pandas as pd


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/git/repository/my-awesome-project/instance/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def import_csv_to_db(csv_file):
    df = pd.read_csv(csv_file, header=0)

    with app.app_context():
        for index, row in df.iterrows():
            try:
                new_data = StudentSpending(
                    user_id=None if pd.isnull(row.get('user_id')) else row.get('user_id'),
                    age=row.get('age', None),
                    gender=row.get('gender', 'Unknown'),
                    year_in_school=row.get('year_in_school', 'Unknown'),
                    major=row.get('major', 'Unknown'),
                    monthly_income=row.get('monthly_income', 0.0),
                    financial_aid=row.get('financial_aid', 0.0),
                    tuition=row.get('tuition', 0.0),
                    housing=row.get('housing', 0.0),
                    food=row.get('food', 0.0),
                    transportation=row.get('transportation', 0.0),
                    books_supplies=row.get('books_supplies', 0.0),
                    entertainment=row.get('entertainment', 0.0),
                    personal_care=row.get('personal_care', 0.0),
                    technology=row.get('technology', 0.0),
                    health_wellness=row.get('health_wellness', 0.0),
                    miscellaneous=row.get('miscellaneous', 0.0),
                    preferred_payment_method=row.get('preferred_payment_method', 'Unknown')
                )
                db.session.add(new_data)
            except Exception as e:
                print(f"Error occurred while adding row {index}: {e}")

        db.session.commit()
        print("Data has been successfully imported.")

if __name__ == '__main__':
    import_csv_to_db('student_spending.csv')
