from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Float, String, Date


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    nickname = db.Column(db.String(100),nullable=True)
    average_income = db.Column(db.Float)
    average_spending = db.Column(db.Float)
    emailaddress = db.Column(db.String(150), nullable=True)
    password = db.Column(db.String(200), nullable=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    year_in_school = db.Column(db.String(50))
    major = db.Column(db.String(100))
    profile_picture = db.Column(db.String(200), nullable=False, default='default_picture.png')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    spendings = db.relationship('Detail', backref='user', lazy=True)
    saving_goals = db.relationship('Saving_Goal', backref='user', lazy=True)
    spendings_records = db.relationship('Record', backref='user', lazy=True)
    def __repr__(self):
        return f"<User {self.username}>"

class Detail(db.Model):
    __tablename__ = 'student_spending_detail'

    detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    living_expense = db.Column(db.Float)
    allowance = db.Column(db.Float)
    income = db.Column(db.Float)
    tuition = db.Column(db.Float)
    housing = db.Column(db.Float)
    food = db.Column(db.Float)
    transportation = db.Column(db.Float)
    study_materials = db.Column(db.Float)
    entertainment = db.Column(db.Float)
    personal_care = db.Column(db.Float)
    technology = db.Column(db.Float)
    apparel = db.Column(db.Float)
    travel = db.Column(db.Float)
    others = db.Column(db.Float)
    preferred_payment_method = db.Column(db.String(50))
    date = db.Column(db.DateTime)

    def __repr__(self):
        return f"<StudentSpending spending_id={self.spending_id}, amount={self.monthly_income}>"
    
class Saving_Goal(db.Model):
    __tablename__ = 'saving_goal'
    saving_goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    name = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False, default=0.0)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    progress = db.Column(db.String(100))
    progress_amount = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f"Saving Goal: {self.saving_goal_id}"
    
class  Record(db.Model):
    __tablename__ = 'record'

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime)
    category = db.Column(db.String(200))
    note = db.Column(db.String(300))

    def __repr__(self):
        return f"Saving Goal: {self.record_id}"


