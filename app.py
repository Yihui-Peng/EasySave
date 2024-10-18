from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/newSpending')
def newSpending():
    return render_template('newSpending.html')

@app.route('/savingGoal')
def savingGoal():
    return render_template('savingGoal.html')

@app.route('/setting')
def setting():
    return render_template('settings.html')

@app.route('/userProfile')
def userProfile():
    return render_template('userProfile.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)