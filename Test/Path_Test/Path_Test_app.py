import pytest
from app import app, db, User, Detail, Saving_Goal, Record
from datetime import datetime


@pytest.fixture
def client():
    """Fixture to configure a test client."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing
    app.config['SECRET_KEY'] = 'test_secret_key'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add test data
            user = User(username="testuser", emailaddress="test@example.com", password="password")
            db.session.add(user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()


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
        assert session['user_id'] is not None

    # Test POST with invalid credentials
    response = client.post('/login', data={'username': 'invalid', 'password': 'invalid'})
    assert response.status_code == 200
    assert b'username or password is incorrect' in response.data


def test_home(client):
    """Test the home route functionality."""
    with client.session_transaction() as session:
        session['user_id'] = 1  # Simulate logged-in user

    response = client.get('/home')
    assert response.status_code == 200
    assert b'Daily Budget' in response.data


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
    assert b'Add New Record' in response.data

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


# cd /d D:\学习资料\Software Development\my-awesome-project

# venv\Scripts\activate

# echo %cd%

# set PYTHONPATH=.

# pytest Test/Path_Test/Path_Test_app.py
