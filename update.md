
### Website Codebase Modification Manual

**1. Database Modifications**

![ER diagram](ER%20Diagram.png)

The database schema has been updated to better organize and manage user data. Below are the key changes:

- **User Table**: This table now centralizes most information related to users such as username, email, and encrypted passwords. 

- **Record Table**: Each entry in this table represents a new record created by a user. Records can represent either income or expenses.

- **Detail Table**: This table provides a monthly summary of records. Records are aggregated by category for each user, ensuring that there is a maximum of one Detail entry per user per month. The date field in each Detail record distinguishes which month the details pertain to.

**ER Diagram**: Please refer to the updated ER diagram included in this manual for a visual representation of the database structure.

**2. Using Data in `app.py`**

Data is primarily accessed using the user's ID. Here’s how you can retrieve and utilize data from the database:

- **Fetching User Data**:
  ```python
  user = User.query.filter_by(user_id=user_id).first()
  ```

- **Fetching the Most Recent Spending Record**:
  ```python
  spending = Record.query.filter_by(user_id=user.user_id).order_by(Record.datum.desc()).first()
  ```

- **Fetching the Current Saving Goal**:
  ```python
  savingGoal = Saving_Goal.query.filter_by(user_id=user.user_id).first()
  ```

- **Fetching Monthly Details**:
  ```python
  details = Detail.query.filter_by(user_id=user.user_id).order_by(Detail.datum.desc()).first()
  ```

**3. Submitting Data**

When creating forms to submit data to the database, ensure the form tag includes an action attribute pointing to the appropriate route in `app.py`.(There are other tags that activate POST to get data, but check for yourself.) For example:

- **Form Example for New Records**:
  ```html
  <form action="/newRecords" method="post" onsubmit="return validateForm()">
  ```

The corresponding route in `app.py` handles the data submitted via the form:

- **Route Example**:
  ```python
  @app.route('/newRecords', methods=['GET', 'POST'])
  ```

**4. Login and Session Management**

The login page is now linked with session management. Accessing personal pages requires user authentication first. Use the following credentials for testing:

- **Username**: test_user1
- **Password**: password1

Once logged in, the user's ID is stored in the session. To retrieve **the currently logged-in user** in `app.py`, use:

```python
user_id = session.get('user_id')
user = User.query.filter_by(user_id=user_id).first()
```

This ensures that the session after login contains the user's ID, which is crucial for fetching personalized data.

