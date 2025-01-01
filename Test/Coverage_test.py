import time
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# TestRail configuration
API_URL = 'https://myawesomeproject6.testrail.io/index.php?/api/v2/'
API_KEY = 'aa6e0Skj1xL0CZDIc5fF-.a.bMYyReOnZunMPSesI'
USER = 's3845567@vuw.leidenuniv.nl'
PROJECT_ID = 1
RUN_ID = 1

# Selenium WebDriver configuration
driver = webdriver.Chrome()


def add_test_result(test_case_id, status, comment=''):
    """
    提交测试结果到 TestRail。
    :param test_case_id: 测试用例 ID
    :param status: 1 = Passed, 5 = Failed
    :param comment: 可选，测试备注
    """
    url = f'{API_URL}add_result_for_case/{RUN_ID}/{test_case_id}'
    data = {
        "status_id": status,  # 1 = Passed, 5 = Failed
        "comment": comment
    }
    response = requests.post(url, auth=(USER, API_KEY), json=data)

    if response.status_code == 200:
        print(f"Successfully updated result for Test Case ID {test_case_id}")
    else:
        print(f"Failed to update result for Test Case ID {test_case_id}, Status Code: {response.status_code}")


def test_register_page():
    try:
        # opening register page
        driver.get("http://127.0.0.1:5000")
        assert "Register" in driver.title, "Error when loading the register page"

        register_link = driver.find_element(By.XPATH, "//p[contains(text(),\"Don't have an account?\")]/a")

        register_link.click()

        time.sleep(2)

        # Ensuring the registration form is shown
        username_field = driver.find_element(By.ID, "new-username")
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "new-password")
        confirm_password_field = driver.find_element(By.ID, "confirm-password")
        register_button = driver.find_element(By.CLASS_NAME, "btn")

        assert username_field.is_displayed(), "username field is not displayed"
        assert email_field.is_displayed(), "email field is not displayed"
        assert password_field.is_displayed(), "password field is not displayed"
        assert confirm_password_field.is_displayed(), "confirm password field is not displayed"
        assert register_button.is_enabled(), "register button field is not displayed"

        style = register_button.get_attribute("style")
        print(f"Button styles: {style}")

        # 1. Testing the result when the password is wrong
        username_field.send_keys("testuser")
        email_field.send_keys("testuser@example.com")
        password_field.send_keys("password123")
        confirm_password_field.send_keys("password124")  # 密码不匹配
        register_button.click()
        
        # Ensuring notification about wrong password
        time.sleep(2)  # waiting for the page to update
        alert_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        assert "Passwords do not match." in alert_message, f"Not showing expected message：{alert_message}"


        username_field.clear()
        email_field.clear()
        password_field.clear()
        confirm_password_field.clear()

        # 2. testing invalid email
        username_field.send_keys("testuser6")
        email_field.send_keys("invalid-email")
        password_field.send_keys("password123")
        confirm_password_field.send_keys("password123")
        register_button.click()

        # Ensuring notification about invalid email
        time.sleep(2)
        alert_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        assert "Invalid email address." in alert_message, f"Not showing expected message：{alert_message}"

        # Emptying input field
        username_field.clear()
        email_field.clear()
        password_field.clear()
        confirm_password_field.clear()

        # Testing existing username or email
        username_field.send_keys("test_user1")
        email_field.send_keys("newuser@example.com")  # 假设这个用户已存在
        password_field.send_keys("password123")
        confirm_password_field.send_keys("password123")
        register_button.click()

        # Ensuring notification about existing username or email
        time.sleep(2)
        alert_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        assert "Username or email already exists" in alert_message, f"Not showing expected message：{alert_message}"


        username_field.clear()
        email_field.clear()
        password_field.clear()
        confirm_password_field.clear()

        # 4. Testing successful registration
        username_field.send_keys("newuser")
        email_field.send_keys("newuser@example.com")
        password_field.send_keys("password123")
        confirm_password_field.send_keys("password123")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn")))
        register_button.click()


        #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn")))


        WebDriverWait(driver, 10).until(EC.url_contains("survey"))
        assert "survey" in driver.current_url, f"didn't go to survey page: {driver.current_url}"

        print("successful registration!")

        # Updating result to testrail page with testcase ID 10
        add_test_result(10, 1, "Registration successful")

    except Exception as e:
        print(f"Test failed due to: {str(e)}")

        # Updating result to testrail page
        add_test_result(10, 5, f"Registration test failed: {str(e)}")

    finally:
        driver.quit()


def test_login_with_invalid_credentials():
    try:
        driver.get("http://127.0.0.1:5000")

        # Input username and password to login
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        # Input wrong username and password
        username_field.send_keys("wrong_user")
        password_field.send_keys("wrong_password")


        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        # Waiting for the page to see if it stays in login page

        WebDriverWait(driver, 10).until(EC.url_contains("login"))

        print("wrong login test successful")

        # Update the test result to testrail with testcase ID 7
        add_test_result(7, 1, "Login failed as expected with incorrect credentials")

    except Exception as e:
        print(f"Test failed due to: {str(e)}")
        add_test_result(7, 5, f"Login failed test failed: {str(e)}")
    finally:
        driver.quit()

def test_login_page():
    try:

        driver = webdriver.Chrome()

        driver.get("http://127.0.0.1:5000")

        # Input username and password to login
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        # Input right username and password
        username_field.send_keys("test_user1")
        password_field.send_keys("password1")
        """
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        assert login_button.is_enabled(), "login button is not enabled"
        login_button.click()"""

        # Submitting login form
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        # Waiting for the page to see if it goes to home page
        time.sleep(2)
        assert "home" in driver.current_url

        # Update the test result to testrail with testcase ID 7
        add_test_result(7, 1, "Login successful")

    except Exception as e:
        print(f"Test failed due to: {str(e)}")
        # Update the test result to testrail with testcase ID 7
        add_test_result(7, 5, f"Login test failed: {str(e)}")
    finally:
        driver.quit()


def test_login_and_add_goal():
    try:
        driver = webdriver.Chrome()

        driver.get("http://127.0.0.1:5000")

        # login
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys("test_user1")
        password_field.send_keys("password1")
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        WebDriverWait(driver, 10).until(EC.url_contains("home"))

        driver.get("http://127.0.0.1:5000/savingGoal")

        # Press the add new goal button
        add_goal_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-goal-btn"))
        )
        add_goal_button.click()


        goal_form = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "goal-form"))
        )

        # entering and save the saving-goal data
        name_field = driver.find_element(By.ID, "name")
        start_date_field = driver.find_element(By.ID, "start-date")
        end_date_field = driver.find_element(By.ID, "end-date")
        amount_field = driver.find_element(By.ID, "amount")
        progress_field = driver.find_element(By.ID, "progress")


        name_field.send_keys("Vacation")
        driver.execute_script("arguments[0].setAttribute('value', '2024-12-01');", start_date_field)
        driver.execute_script("arguments[0].setAttribute('value', '2025-12-01');", end_date_field)
        amount_field.send_keys("5000")
        progress_field.send_keys("finished")

        # Submitting saving goal
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # making sure the new saving goal is saved and shown
        goal_rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//table[@class='records-table']/tbody/tr"))
        )
        print("Saving goal added successfully")

        # Update the test result to testrail with testcase ID 6
        add_test_result(6, 1, "Goal added successfully")

    except Exception as e:
        print(f"Test failed due to: {str(e)}")
        add_test_result(6, 5, f"Goal addition failed: {str(e)}")
    finally:
        driver.quit()

def test_new_records():
    try:
        driver = webdriver.Chrome()

        driver.get("http://127.0.0.1:5000")

        # login
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys("test_user1")
        password_field.send_keys("password1")
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()


        WebDriverWait(driver, 10).until(EC.url_contains("home"))

        # Opening the newRecord page
        driver.get("http://127.0.0.1:5000/newRecords")

        # making sure the input form is shown correctly
        amount_field = driver.find_element(By.ID, "amount")
        category_level_1_field = driver.find_element(By.ID, "category-level-1")
        category_level_2_field = driver.find_element(By.ID, "category-level-2")
        date_field = driver.find_element(By.ID, "date")
        note_field = driver.find_element(By.ID, "note")

        assert amount_field.is_displayed(), "amount is not displayed"
        assert category_level_1_field.is_displayed(), "level 1 category field is not displayed"
        assert category_level_2_field.is_displayed(), "level 2 category field is not displayed"
        assert date_field.is_displayed(), "date field is not displayed"
        assert note_field.is_displayed(), "note field is not displayed"

        # input in the form
        amount_field.send_keys("100.50")
        category_level_1_field.send_keys("Necessities")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "category-level-2")))

        # choosing sue sub-category
        category_level_2_field.send_keys("Housing")
        driver.execute_script("arguments[0].setAttribute('value', '2024-12-01');", date_field)
        note_field.send_keys("This is a test record.")


        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Ensure the data is submitted successfully
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert_text = alert.text
        assert alert_text == "New record added successfully", f"Expected alert text not found. Got: {alert_text}"
        alert.accept()

        # Update the test result to testrail with testcase ID 8
        add_test_result(8, 1, "Record added successfully")

    except Exception as e:
        add_test_result(8, 5, f"New record test failed: {str(e)}")

    finally:
        driver.quit()


def test_settings_page():
    try:
        driver = webdriver.Chrome()

        driver.get("http://127.0.0.1:5000")

        # login
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys("test_user1")
        password_field.send_keys("password1")
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        WebDriverWait(driver, 10).until(EC.url_contains("home"))

        # Setting page
        driver.get("http://127.0.0.1:5000/setting")

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "menu")))

        # Account Security part
        account_security_button = driver.find_element(By.XPATH, "//div[text()='2: Account Security']")
        account_security_button.click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "account-section")))

        # Test changing username
        change_username_button = driver.find_element(By.XPATH, "//div[text()='1: Change Username']")
        change_username_button.click()

        new_username_field = driver.find_element(By.ID, "new_username")
        new_username_field.clear()
        new_username_field.send_keys("new_username123")
        submit_button = driver.find_element(By.ID, "submit_username")
        submit_button.click()

        # Check if username is updated
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == "Username updated successfully."
        alert.accept()

        # Test changing email
        change_email_button = driver.find_element(By.XPATH, "//div[text()='2: Change Email']")
        change_email_button.click()

        new_email_field = driver.find_element(By.ID, "new_email")
        new_email_field.clear()
        new_email_field.send_keys("new_email@example.com")
        submit_email_button = driver.find_element(By.ID, "submit_email")
        submit_email_button.click()

        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == "Email updated successfully."
        alert.accept()

        # Test changing password
        change_password_button = driver.find_element(By.XPATH, "//div[text()='4: Change Password']")
        change_password_button.click()

        current_password_field = driver.find_element(By.ID, "current_password")
        new_password_field = driver.find_element(By.ID, "new_password")
        confirm_password_field = driver.find_element(By.ID, "confirm_password")

        current_password_field.send_keys("password1")
        new_password_field.send_keys("new_password123")
        confirm_password_field.send_keys("new_password123")
        submit_password_button = driver.find_element(By.ID, "submit_password")
        submit_password_button.click()

        # Check if password is updated successfully
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == "Password updated successfully."
        alert.accept()

        # Test changing nickname
        change_nickname_button = driver.find_element(By.XPATH, "//div[text()='3: Change Nickname']")
        change_nickname_button.click()

        new_nickname_field = driver.find_element(By.ID, "new_nickname")
        new_nickname_field.clear()
        new_nickname_field.send_keys("new_nickname123")
        submit_nickname_button = driver.find_element(By.ID, "submit_nickname")
        submit_nickname_button.click()


        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == "Nickname updated successfully."
        alert.accept()


    except Exception as e:
        print(f"Test failed due to: {str(e)}")

    finally:
        driver.quit()



def test_user_profile_update():
    try:
        driver = webdriver.Chrome()

        # login
        driver.get("http://127.0.0.1:5000")
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")


        username_field.send_keys("test_user1")
        password_field.send_keys("password1")

        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        WebDriverWait(driver, 10).until(EC.url_contains("home"))
        print("登录成功")

        # userProfile page
        driver.get("http://127.0.0.1:5000/userProfile")


        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "profile-container")))

        # Test if the data is shown correctly
        username_value = driver.find_element(By.ID, "username").get_attribute("value")
        assert username_value == "test_user1", f"wrong username, expecting 'test_user1', showing {username_value}"

        gender_value = driver.find_element(By.ID, "gender").get_attribute("value")
        assert gender_value == "alien", f"wrong gender, expecting 'Alien', showing {gender_value}"

        nickname_value = driver.find_element(By.ID, "nickname").get_attribute("value")
        assert nickname_value == "tester1", f"wrong nickname, expecting 'Tester', showing {nickname_value}"

        # changing user nickname
        new_nickname = "NewNickname"
        driver.find_element(By.ID, "nickname").clear()
        driver.find_element(By.ID, "nickname").send_keys(new_nickname)

        # Changeing the gender
        gender_dropdown = driver.find_element(By.ID, "gender")
        gender_dropdown.click()
        gender_dropdown.find_element(By.XPATH, "//option[@value='male']").click()

        # Submitting the new nickname and gender
        save_button = driver.find_element(By.CLASS_NAME, "save-btn")
        save_button.click()

        # Reloading the page
        driver.get("http://127.0.0.1:5000/userProfile")

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "profile-container")))

        updated_nickname_value = driver.find_element(By.ID, "nickname").get_attribute("value")
        assert updated_nickname_value == new_nickname, f"nickname update failed, expecting '{new_nickname}', showing {updated_nickname_value}"

        updated_gender_value = driver.find_element(By.ID, "gender").get_attribute("value")
        assert updated_nickname_value == new_nickname, f"gender update failed, expecting '{new_nickname}', showing {updated_nickname_value}"

        print("username profile successful")

        # Uploading the result to testrail with testcase ID 9
        add_test_result(9, 1, "User profile updated successfully")

    except Exception as e:
        print(f"test fail dute to {str(e)}")
        add_test_result(9, 5, f"User profile updated due to: {str(e)}")

    finally:
        driver.quit()







# 执行测试
#test_login_with_invalid_credentials()
#test_login_and_add_goal()
#test_new_records()
#test_settings_page()
#test_user_profile_update()
#test_login_page()
#test_register_page()
