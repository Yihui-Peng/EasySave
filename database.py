from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    _tablename_= 'User'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    emailadress = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    spendings = db.relationship('StudentSpending', backref='user', lazy=True)
    logins = db.relationship('Login', backref='user', lazy=True)
    
    def __repr__(self):
        return f"<User {self.username}>"


class StudentSpending(db.Model):
    spending_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    year_in_school = db.Column(db.String(50))
    major = db.Column(db.String(100))
    monthly_income = db.Column(db.Float)
    financial_aid = db.Column(db.Float)
    tuition = db.Column(db.Float)
    housing = db.Column(db.Float)
    food = db.Column(db.Float)
    transportation = db.Column(db.Float)
    books_supplies = db.Column(db.Float)
    entertainment = db.Column(db.Float)
    personal_care = db.Column(db.Float)
    technology = db.Column(db.Float)
    health_wellness = db.Column(db.Float)
    miscellaneous = db.Column(db.Float)
    preferred_payment_method = db.Column(db.String(50))

    def __repr__(self):
        return f"<StudentSpending spending_id={self.spending_id}, amount={self.monthly_income}>"