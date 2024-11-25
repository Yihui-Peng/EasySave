import unittest
from app import app, db
from database import User
import os


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client and initialize a fresh in-memory database."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            # Create a test user
            test_user = User(username='testuser', emailaddress='test@example.com', password='password123')
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # 1. Testing the /login Route
    def test_login_success(self):
        """Test logging in with correct credentials."""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)  # Adjust based on your home page content

    def test_login_incorrect_username(self):
        """Test logging in with an incorrect username."""
        response = self.client.post('/login', data={
            'username': 'wronguser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password is incorrect', response.data)

    def test_login_incorrect_password(self):
        """Test logging in with an incorrect password."""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password is incorrect', response.data)

    def test_login_missing_fields(self):
        """Test logging in with missing username and password."""
        response = self.client.post('/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password is incorrect', response.data)

    # 2. Testing the /register Route
    def test_register_success(self):
        """Test successful user registration."""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'confirm-password': 'newpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)  # Adjust based on flash message

    def test_register_password_mismatch(self):
        """Test registration with password mismatch."""
        response = self.client.post('/register', data={
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password': 'password1',
            'confirm-password': 'password2'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords do not match', response.data)

    def test_register_invalid_email(self):
        """Test registration with invalid email address."""
        response = self.client.post('/register', data={
            'username': 'newuser3',
            'email': 'invalidemail',
            'password': 'password123',
            'confirm-password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email address', response.data)

    def test_register_existing_username(self):
        """Test registration with an existing username."""
        # First, register a user
        self.client.post('/register', data={
            'username': 'existinguser',
            'email': 'existing@example.com',
            'password': 'password123',
            'confirm-password': 'password123'
        }, follow_redirects=True)
        # Attempt to register another user with the same username
        response = self.client.post('/register', data={
            'username': 'existinguser',  # Existing username
            'email': 'uniqueemail@example.com',
            'password': 'password123',
            'confirm-password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username or email already exists', response.data)

    def test_register_existing_email(self):
        """Test registration with an existing email."""
        # First, register a user
        self.client.post('/register', data={
            'username': 'uniqueuser',
            'email': 'existingemail@example.com',
            'password': 'password123',
            'confirm-password': 'password123'
        }, follow_redirects=True)
        # Attempt to register another user with the same email
        response = self.client.post('/register', data={
            'username': 'anotheruser',
            'email': 'existingemail@example.com',  # Existing email
            'password': 'password123',
            'confirm-password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username or email already exists', response.data)

    def test_register_missing_fields(self):
        """Test registration with missing fields."""
        response = self.client.post('/register', data={
            'username': '',
            'email': '',
            'password': '',
            'confirm-password': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Depending on your validation, adjust the expected message
        self.assertIn(b'Passwords do not match', response.data) or self.assertIn(b'Invalid email address',
                                                                                 response.data)

    # 3. Testing the /home Route
    def test_home_logged_in(self):
        """Test accessing home page when logged in and user exists."""
        # Log in first
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        # Access home
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)  # Adjust based on your home page content

    def test_home_not_logged_in(self):
        """Test accessing home page when not logged in."""
        response = self.client.get('/home', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login.html', response.data)  # Adjust based on your login template

    def test_home_user_not_exists(self):
        """Test accessing home page when user does not exist."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 9999  # Assuming this user_id does not exist
        response = self.client.get('/home', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User not found.', response.data)

    def test_home_saving_goal_exists(self):
        """Test accessing home page when a saving goal exists."""
        # Log in first
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        # Add a saving goal
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            saving_goal = Saving_Goal(
                user_id=user.user_id,
                amount=1000.0,
                start_date='2024-01-01',
                end_date='2024-12-31',
                progress='In Progress',
                progress_amount=500.0
            )
            db.session.add(saving_goal)
            db.session.commit()
        # Access home
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Saving Goal', response.data)  # Adjust based on your template

    def test_home_saving_goal_not_exists(self):
        """Test accessing home page when no saving goal exists."""
        # Log in first
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        # Ensure no saving goals exist
        with app.app_context():
            Saving_Goal.query.delete()
            db.session.commit()
        # Access home
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Default to 20%', response.data)  # Adjust based on your template

    # 4. Testing the /newRecords Route
    def test_new_records_get_logged_in(self):
        """Test accessing newRecords page when logged in."""
        # Log in first
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        # Access newRecords
        response = self.client.get('/newRecords')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'newRecords.html', response.data)  # Adjust based on your template

    def test_new_records_get_not_logged_in(self):
        """Test accessing newRecords page when not logged in."""
        response = self.client.get('/newRecords', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login.html', response.data)  # Adjust based on your login template

    def test_new_records_post_valid(self):
        """Test submitting a valid new record."""
        # Log in first
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        # Submit new record
        response = self.client.post('/newRecords', data={
            'amount': '100.50',
            'category-level-1': 'Necessities',
            'category-level-2': 'Housing',
            'date': '2024-05-15',
            'note': 'Monthly rent'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Check if redirected correctly (since flash message is commented out, adjust accordingly)
        # For example, check if the new record appears in the response
        self.assertIn(b'Monthly rent', response.data)

    def test_new_records_post_missing_fields(self):
        """Test submitting a new record with missing fields."""
        # Log in first
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        # Submit incomplete data
        response = self.client.post('/newRecords', data={
            'amount': '',
            'category-level-1': '',
            'category-level-2': '',
            'date': '',
            'note': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please fill out all required fields', response.data)

    def test_new_records_post_invalid_date(self):
        """Test submitting a new record with invalid date format."""
        # Log in first
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        # Submit invalid date
        response = self.client.post('/newRecords', data={
            'amount': '50.00',
            'category-level-1': 'Flexible_spending',
            'category-level-2': 'Entertainment',
            'date': '15-05-2024',  # Invalid format
            'note': 'Movie tickets'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid date format', response.data)


if __name__ == '__main__':
    unittest.main()
