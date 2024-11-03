from flask import Flask
from database import db, StudentSpending
import pandas as pd


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/git/repository/my-awesome-project/instance/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def import_csv_to_db(csv_file):
    # 使用 pandas 读取 CSV 文件
    df = pd.read_csv(csv_file)

    with app.app_context():
        for index, row in df.iterrows():
            new_data = StudentSpending(
                age=row['age'],
                gender=row['gender'],
                year_in_school=row['year_in_school'],
                major=row['major'],
                monthly_income=row['monthly_income'],
                financial_aid=row['financial_aid'],
                tuition=row['tuition'],
                housing=row['housing'],
                food=row['food'],
                transportation=row['transportation'],
                books_supplies=row['books_supplies'],
                entertainment=row['entertainment'],
                personal_care=row['personal_care'],
                technology=row['technology'],
                health_wellness=row['health_wellness'],
                miscellaneous=row['miscellaneous'],
                preferred_payment_method=row['preferred_payment_method']
            )
            db.session.add(new_data)

        db.session.commit()
        print("Data has been successfully imported.")

if __name__ == '__main__':
    import_csv_to_db('student_spending.csv')
