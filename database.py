from flask_sqlalchemy import SQLAlchemy

#  New adding, not sure if it is necessary
from database import db
from sqlalchemy import Column, Integer, Float, String, Date


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    nickname = db.Column(db.String(100),nullable=True)
    emailadress = db.Column(db.String(150), nullable=True)
    password = db.Column(db.String(200), nullable=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    year_in_school = db.Column(db.String(50))
    major = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    spendings = db.relationship('StudentSpending', backref='user', lazy=True)
    saving_goals = db.relationship('Saving_Goal', backref='user', lazy=True)
    spendings_records = db.relationship('Spending', backref='user', lazy=True)
    def __repr__(self):
        return f"<User {self.username}>"

class StudentSpending(db.Model):
    __tablename__ = 'student_spending'

    spending_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    disposable_income = db.Column(db.Float)
    tuition = db.Column(db.Float)
    housing = db.Column(db.Float)
    food = db.Column(db.Float)
    transportation = db.Column(db.Float)
    books_supplies = db.Column(db.Float)
    entertainment = db.Column(db.Float)
    personal_care = db.Column(db.Float)
    technology = db.Column(db.Float)
    others = db.Column(db.Float)
    preferred_payment_method = db.Column(db.String(50))

    def __repr__(self):
        return f"<StudentSpending spending_id={self.spending_id}, amount={self.monthly_income}>"
    
class Saving_Goal(db.Model):
    __tablename__ = 'saving_goal'

    saving_goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    amount = db.Column(db.Float)
    start_datum = db.Column(db.DateTime)
    end_datum = db.Column(db.DateTime)
    progress = db.Column(db.String(100))
    progress_amount = db.Column(db.Float)

    def __repr__(self):
        return f"Saving Goal: {self.saving_goal_id}"

   
# Changed the spending to Records, the Records part is finished
class Records(db.Model):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    category_level_1 = Column(String(50), nullable=False)
    category_level_2 = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String(255), nullable=True)

    def __repr__(self):
        return f"Saving Goal: {self.spending}"


