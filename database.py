from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StudentSpending(db.Model):
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
        return f"<StudentSpending {self.age}, {self.gender}, {self.year_in_school}>"