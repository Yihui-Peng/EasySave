import pytest
from app import app, db, User, Detail, Saving_Goal, Record
from import_database import initialize_database
from datetime import datetime


@pytest.fixture
def client():
    """Fixture to configure a test client."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add sample user for testing
            user = User(username='testuser', emailaddress='test@example.com', password='password')
            db.session.add(user)
            db.session.commit()
        yield client

        with app.app_context():
            db.drop_all()


# ---------------- Path Testing for checking the users who didn't login ----------

def test_protected_route_without_login(client):
    """Test accessing protected routes without logging in."""
    response = client.get('/details_and_charts')
    assert response.status_code == 302  # Redirect to login



# ---------------- Path Testing for Routes ----------------

def test_login(client):
    """Test the login route functionality."""
    # Test GET request to the login page
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Username' in response.data

    # Test POST with valid credentials
    response = client.post('/login', data={'username': 'testuser', 'password': 'password'})
    assert response.status_code == 302  # Redirect to home
    with client.session_transaction() as session:
        # assert session['user_id'] is not None
        assert session['user_id'] == 1

    # Test POST with invalid credentials
    response = client.post('/login', data={'username': 'invalid', 'password': 'invalid'})
    assert response.status_code == 200
    assert b'username or password is incorrect' in response.data


def test_home(client):
    """Test the home route functionality."""
    valid_user_id = 1  # Existing user ID

    with client.session_transaction() as session:
        session['user_id'] = valid_user_id

    response = client.get('/home')
    assert response.status_code == 200
    assert b'Daily Budget' in response.data



# ---------------- Path Testing for input validation ----------

def test_new_record_input_validation(client):
    """Test validation for new spending records."""
    with client.session_transaction() as session:
        session['user_id'] = 1  # Simulate logged-in user

    # Test missing fields
    response = client.post('/newRecords', data={
        'amount': '',
        'category-level-1': 'Necessities',
        'category-level-2': '',
        'date': '2024-01-01'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"All fields must be filled out" in response.data

    # Test negative amount
    response = client.post('/newRecords', data={
        'amount': -100,
        'category-level-1': 'Necessities',
        'category-level-2': 'housing',
        'date': '2024-01-01'
    })
    assert response.status_code == 200
    assert b"Amount must be a positive value" in response.data

    # Test valid input
    response = client.post('/newRecords', data={
        'amount': 150,
        'category-level-1': 'Necessities',
        'category-level-2': 'housing',
        'date': '2024-01-01'
    })
    assert response.status_code == 302  # Redirect on successful submission
    with client.session_transaction():
        record = Record.query.filter_by(user_id=1, amount=150, category='Necessities:housing').first()
        assert record is not None




# ---------------- Path Testing for filter functionality ----------------

def test_filter_functionality(client):
    """Test filtering functionality in details_and_charts."""
    with client.session_transaction() as session:
        session['user_id'] = 1  # Simulate a logged-in user

    # Test valid category selection
    response = client.post('/details_and_charts', data={
        'category_level_1': 'Necessities',
        'category_level_2': 'housing'
    })
    assert response.status_code == 200
    assert b"Housing" in response.data  # Check if response contains "Housing"

    # Test invalid category input
    response = client.post('/details_and_charts', data={
        'category_level_1': 'Invalid_Category',
        'category_level_2': 'Nonexistent_Subcategory'
    })
    assert response.status_code == 400  # Expecting a bad request or error handling



def test_logout(client):
    """Test the logout functionality."""
    with client.session_transaction() as session:
        session['user_id'] = 1  # Simulate logged-in user

    response = client.get('/logout')
    assert response.status_code == 302  # Redirect to login
    with client.session_transaction() as session:
        assert 'user_id' not in session


def test_data_endpoint(client):
    """Test the /data route to ensure it returns correct data."""
    with client.session_transaction() as session:
        session['user_id'] = 1  # Simulate logged-in user

    response = client.get('/data')
    assert response.status_code == 200
    assert b'Username' in response.data


def test_new_records(client):
    """Test the newRecords route functionality."""
    with client.session_transaction() as session:
        session['user_id'] = 1  # Simulate logged-in user

    response = client.get('/newRecords')
    assert response.status_code == 200
    assert b'Create New Record' in response.data

    response = client.post('/newRecords', data={
        'amount': '100',
        'category-level-1': 'Necessities',
        'category-level-2': 'Food',
        'date': '2025-01-01',
        'note': 'Test note'
    })
    assert response.status_code == 302  # Redirect after POST


def test_details_and_charts(client):
    """Test the /details_and_charts route functionality."""
    with client.session_transaction() as session:
        session['user_id'] = 1  # Simulate logged-in user

    response = client.get('/details_and_charts')
    assert response.status_code == 200
    assert b'Spending Records' in response.data
    assert b'Spending Distribution Chart' not in response.data 


def test_budget(client):
    """Test the budget route functionality."""
    with client.session_transaction() as session:
        session['user_id'] = 1  # Simulate logged-in user

    response = client.get('/budget')
    assert response.status_code == 200
    assert b'Budget Allocation' in response.data


# ---------------- Database Operations Testing ----------------

def test_initialize_database(client):
    """Test database initialization logic."""
    with client.application.app_context():
        db.create_all()
        initialize_database()
        users = User.query.all()
        assert len(users) > 0  # Ensure users were created


def test_add_data_to_database(client):
    """Test adding data to the database."""
    with client.application.app_context():
        new_user = User(username="newtestuser", emailaddress="newtest@example.com", password="newpassword")
        db.session.add(new_user)
        db.session.commit()

        user = User.query.filter_by(username="newtestuser").first()
        assert user is not None
        assert user.emailaddress == "newtest@example.com"


def test_remove_data_from_database(client):
    """Test removing data from the database."""
    with client.application.app_context():
        user = User.query.filter_by(username="testuser").first()
        db.session.delete(user)
        db.session.commit()

        user = User.query.filter_by(username="testuser").first()
        assert user is None



# cd /d D:\学习资料\Software Development\my-awesome-project

# venv\Scripts\activate

# echo %cd%

# set PYTHONPATH=.

# pytest Test/Path_Test_combined.py
