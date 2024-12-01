import time
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# TestRail 配置
API_URL = 'https://myawesomeproject6.testrail.io/index.php?/api/v2/'
API_KEY = 'aa6e0Skj1xL0CZDIc5fF-.a.bMYyReOnZunMPSesI'  # 从 TestRail 获取的 API 密钥
USER = 's3845567@vuw.leidenuniv.nl'  # TestRail 登录邮箱
PROJECT_ID = 1  # 项目 ID
RUN_ID = 1  # 测试执行 ID

# Selenium WebDriver 配置
driver = webdriver.Chrome()  # 使用 Chrome 浏览器


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
        # 打开注册页面
        driver.get("http://127.0.0.1:5000")  # 根据你的 Flask 应用地址更新
        assert "Register" in driver.title, "注册页面加载失败，页面标题不正确"

        register_link = driver.find_element(By.XPATH, "//p[contains(text(),\"Don't have an account?\")]/a")

        register_link.click()

        time.sleep(2)

        # 确保注册表单元素显示
        username_field = driver.find_element(By.ID, "new-username")
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "new-password")
        confirm_password_field = driver.find_element(By.ID, "confirm-password")
        register_button = driver.find_element(By.CLASS_NAME, "btn")

        assert username_field.is_displayed(), "用户名字段未显示"
        assert email_field.is_displayed(), "邮箱字段未显示"
        assert password_field.is_displayed(), "密码字段未显示"
        assert confirm_password_field.is_displayed(), "确认密码字段未显示"
        assert register_button.is_enabled(), "注册按钮未启用"

        style = register_button.get_attribute("style")
        print(f"Button styles: {style}")

        # 1. 测试密码不匹配
        username_field.send_keys("testuser")
        email_field.send_keys("testuser@example.com")
        password_field.send_keys("password123")
        confirm_password_field.send_keys("password124")  # 密码不匹配
        register_button.click()
        
        # 确认提示密码不匹配
        time.sleep(2)  # 等待页面更新
        alert_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        assert "Passwords do not match." in alert_message, f"未显示预期错误消息：{alert_message}"


        username_field.clear()
        email_field.clear()
        password_field.clear()
        confirm_password_field.clear()

        # 2. 测试无效邮箱格式
        username_field.send_keys("testuser6")
        email_field.send_keys("invalid-email")  # 无效的邮箱
        password_field.send_keys("password123")
        confirm_password_field.send_keys("password123")
        register_button.click()

        # 确认提示无效邮箱格式
        time.sleep(2)  # 等待页面更新
        alert_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        assert "Invalid email address." in alert_message, f"未显示预期错误消息：{alert_message}"

        # 清空输入框
        username_field.clear()
        email_field.clear()
        password_field.clear()
        confirm_password_field.clear()

        # 3. 测试已存在用户名或邮箱
        username_field.send_keys("test_user1")
        email_field.send_keys("newuser@example.com")  # 假设这个用户已存在
        password_field.send_keys("password123")
        confirm_password_field.send_keys("password123")
        register_button.click()

        # 确认提示用户名或邮箱已存在
        time.sleep(2)  # 等待页面更新
        alert_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        assert "Username or email already exists" in alert_message, f"未显示预期错误消息：{alert_message}"

        # 清空输入框
        username_field.clear()
        email_field.clear()
        password_field.clear()
        confirm_password_field.clear()

        # 4. 测试成功注册
        username_field.send_keys("newuser")
        email_field.send_keys("newuser@example.com")
        password_field.send_keys("password123")
        confirm_password_field.send_keys("password123")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn")))
        register_button.click()


        #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn")))

        # 等待页面跳转并检查是否成功跳转到问卷页面
        WebDriverWait(driver, 10).until(EC.url_contains("survey"))
        assert "survey" in driver.current_url, f"未跳转到问卷页面，当前URL: {driver.current_url}"

        print("注册成功！")

        # 记录测试结果到 TestRail：假设测试用例 ID 为 2
        add_test_result(10, 1, "Registration successful")  # 测试通过，提交到 TestRail

    except Exception as e:
        print(f"Test failed due to: {str(e)}")

        # 记录测试结果到 TestRail：测试失败
        add_test_result(10, 5, f"Registration test failed: {str(e)}")  # 测试失败，提交到 TestRail

    finally:
        # 关闭浏览器
        driver.quit()


def test_login_with_invalid_credentials():
    try:
        # 打开 Flask 登录页面
        driver.get("http://127.0.0.1:5000")

        # 输入用户名和密码并登录
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        # 输入错误的用户名和密码
        username_field.send_keys("wrong_user")
        password_field.send_keys("wrong_password")

        # 提交登录表单
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        # 等待页面加载并检查是否返回到登录页

        WebDriverWait(driver, 10).until(EC.url_contains("login"))

        print("错误登录测试成功！")

        # 记录测试结果到 TestRail：假设测试用例 ID 为 8
        add_test_result(7, 1, "Login failed as expected with incorrect credentials")  # 测试通过，提交到 TestRail

    except Exception as e:
        print(f"Test failed due to: {str(e)}")
        # 记录测试结果到 TestRail：测试失败
        add_test_result(7, 5, f"Login failed test failed: {str(e)}")  # 测试失败，提交到 TestRail
    finally:
        # 关闭浏览器
        driver.quit()

def test_login_page():
    try:

        driver = webdriver.Chrome()

        driver.get("http://127.0.0.1:5000")  # 根据你的 Flask 应用地址更新

        # 输入用户名和密码并登录
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        # 输入用户名和密码
        username_field.send_keys("test_user1")
        password_field.send_keys("password1")
        """
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        assert login_button.is_enabled(), "login button is not enabled"
        login_button.click()"""

        # 提交登录表单
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        # 等待页面跳转并检查是否登录成功
        time.sleep(2)  # 等待一会儿，确保页面加载
        assert "home" in driver.current_url  # 确保跳转到主页

        # 记录测试结果到 TestRail：假设测试用例 ID 为 1
        add_test_result(7, 1, "Login successful")  # 测试通过，提交到 TestRail

    except Exception as e:
        print(f"Test failed due to: {str(e)}")
        # 记录测试结果到 TestRail：测试失败
        add_test_result(7, 5, f"Login test failed: {str(e)}")  # 测试失败，提交到 TestRail
    finally:
        # 关闭浏览器
        driver.quit()


def test_login_and_add_goal():
    try:
        # 初始化 WebDriver（例如使用 Chrome 浏览器）
        driver = webdriver.Chrome()

        # 1. 打开 Flask 登录页面
        driver.get("http://127.0.0.1:5000")  # 根据你的 Flask 应用地址更新

        # 登录步骤
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys("test_user1")  # 假设用户名为 "test_user1"
        password_field.send_keys("password1")  # 假设密码为 "password1"
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        # 等待页面跳转，确认登录成功
        WebDriverWait(driver, 10).until(EC.url_contains("home"))

        # 打开保存目标页面
        driver.get("http://127.0.0.1:5000/savingGoal")

        # 等待并点击“Add a new goal”按钮
        add_goal_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-goal-btn"))
        )
        add_goal_button.click()

        # 等待目标表单显示
        goal_form = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "goal-form"))
        )

        # 输入保存目标数据
        name_field = driver.find_element(By.ID, "name")
        start_date_field = driver.find_element(By.ID, "start-date")
        end_date_field = driver.find_element(By.ID, "end-date")
        amount_field = driver.find_element(By.ID, "amount")
        progress_field = driver.find_element(By.ID, "progress")

        # 填写保存目标数据
        name_field.send_keys("Vacation")
        driver.execute_script("arguments[0].setAttribute('value', '2024-12-01');", start_date_field)
        driver.execute_script("arguments[0].setAttribute('value', '2025-12-01');", end_date_field)
        amount_field.send_keys("5000")
        progress_field.send_keys("finished")

        # 提交保存目标表单
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # 确保页面已加载并且表格中的目标数据已经显示
        goal_rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//table[@class='records-table']/tbody/tr"))
        )
        print("保存目标添加成功！")

        # 记录测试结果到 TestRail：假设测试用例 ID 为 2
        add_test_result(6, 1, "Goal added successfully")  # 测试通过，提交到 TestRail

    except Exception as e:
        print(f"Test failed due to: {str(e)}")
        # 记录测试结果到 TestRail：测试失败
        add_test_result(6, 5, f"Goal addition failed: {str(e)}")  # 测试失败，提交到 TestRail
    finally:
        # 关闭浏览器
        driver.quit()

def test_new_records():
    try:
        # 初始化 WebDriver（例如使用 Chrome 浏览器）
        driver = webdriver.Chrome()

        # 1. 打开 Flask 登录页面
        driver.get("http://127.0.0.1:5000")  # 根据你的 Flask 应用地址更新

        # 登录步骤
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys("test_user1")  # 假设用户名为 "test_user1"
        password_field.send_keys("password1")  # 假设密码为 "password1"
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        # 等待页面跳转，确认登录成功
        WebDriverWait(driver, 10).until(EC.url_contains("home"))

        # 2. 打开 newRecords 页面
        driver.get("http://127.0.0.1:5000/newRecords")

        # 3. 填写表单数据
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

        # 填写表单数据
        amount_field.send_keys("100.50")
        category_level_1_field.send_keys("Necessities")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "category-level-2")))

        # 手动选择子类别（假设在选择了 "Necessities" 后子类别选择框变得可用）
        category_level_2_field.send_keys("Housing")
        driver.execute_script("arguments[0].setAttribute('value', '2024-12-01');", date_field)
        note_field.send_keys("This is a test record.")

        # 提交表单
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # 4. 确认记录已成功添加
        time.sleep(2)  # 等待页面刷新
        # 4. 等待弹出 Alert 并处理
        WebDriverWait(driver, 10).until(EC.alert_is_present())  # 等待弹窗出现
        alert = driver.switch_to.alert  # 切换到弹窗
        alert_text = alert.text
        assert alert_text == "New record added successfully", f"Expected alert text not found. Got: {alert_text}"
        alert.accept()  # 关闭弹窗

        # 记录测试结果到 TestRail
        add_test_result(8, 1, "Record added successfully")  # 测试通过，提交到 TestRail

    except Exception as e:

        # 记录测试结果到 TestRail：测试失败
        add_test_result(8, 5, f"New record test failed: {str(e)}")  # 测试失败，提交到 TestRail

    finally:
        # 关闭浏览器
        driver.quit()


def test_settings_page():
    try:
        # 设置 WebDriver (以 Chrome 为例)
        driver = webdriver.Chrome()

        # 1. 登录流程
        driver.get("http://127.0.0.1:5000")  # 假设首页为登录页

        # 输入用户名和密码并登录
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys("test_user1")
        password_field.send_keys("password1")
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        # 等待页面跳转并确认已登录
        WebDriverWait(driver, 10).until(EC.url_contains("home"))
        print("登录成功！")

        # 2. 访问设置页面
        driver.get("http://127.0.0.1:5000/setting")

        # 确认页面加载完成，检查是否进入设置页
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "menu")))

        # 3. 进入 Account Security 部分
        account_security_button = driver.find_element(By.XPATH, "//div[text()='2: Account Security']")
        account_security_button.click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "account-section")))

        # 4. 测试修改用户名
        change_username_button = driver.find_element(By.XPATH, "//div[text()='1: Change Username']")
        change_username_button.click()

        # 假设有一个文本框用于输入新用户名
        new_username_field = driver.find_element(By.ID, "new_username")  # 假设前端有个ID为 new_username 的输入框
        new_username_field.clear()
        new_username_field.send_keys("new_username123")
        submit_button = driver.find_element(By.ID, "submit_username")  # 假设有一个提交按钮
        submit_button.click()

        # 等待提交结果
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == "Username updated successfully."  # 验证用户名更新成功
        alert.accept()  # 关闭弹窗

        # 5. 测试修改邮箱
        change_email_button = driver.find_element(By.XPATH, "//div[text()='2: Change Email']")
        change_email_button.click()

        new_email_field = driver.find_element(By.ID, "new_email")  # 假设前端有一个ID为 new_email 的输入框
        new_email_field.clear()
        new_email_field.send_keys("new_email@example.com")
        submit_email_button = driver.find_element(By.ID, "submit_email")  # 提交按钮
        submit_email_button.click()

        # 等待提交结果
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == "Email updated successfully."  # 验证邮箱更新成功
        alert.accept()  # 关闭弹窗

        # 6. 测试修改密码
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

        # 等待提交结果
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == "Password updated successfully."  # 验证密码更新成功
        alert.accept()  # 关闭弹窗

        # 7. 测试修改昵称
        change_nickname_button = driver.find_element(By.XPATH, "//div[text()='3: Change Nickname']")
        change_nickname_button.click()

        new_nickname_field = driver.find_element(By.ID, "new_nickname")  # 假设前端有一个ID为 new_nickname 的输入框
        new_nickname_field.clear()
        new_nickname_field.send_keys("new_nickname123")
        submit_nickname_button = driver.find_element(By.ID, "submit_nickname")  # 提交按钮
        submit_nickname_button.click()

        # 等待提交结果
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == "Nickname updated successfully."  # 验证昵称更新成功
        alert.accept()  # 关闭弹窗

        # 8. 测试未登录访问设置页时会被重定向
        driver.quit()  # 退出当前会话

        # 重新启动浏览器并访问设置页面，模拟未登录状态
        driver = webdriver.Chrome()
        driver.get("http://127.0.0.1:5000/setting")

        # 等待页面跳转并确认重定向到登录页面
        WebDriverWait(driver, 10).until(EC.url_contains("login"))
        print("未登录时成功重定向到登录页")

    except Exception as e:
        print(f"Test failed due to: {str(e)}")

    finally:
        driver.quit()



def test_user_profile_update():
    try:
        # 设置WebDriver（以Chrome为例）
        driver = webdriver.Chrome()  # 设置你自己下载的chromedriver路径

        # 1. 登录到网站
        driver.get("http://127.0.0.1:5000")  # 假设登录页面是主页
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        # 输入测试用户名和密码
        username_field.send_keys("test_user1")
        password_field.send_keys("password1")

        # 提交登录表单
        login_button = driver.find_element(By.CLASS_NAME, "btn")
        login_button.click()

        # 等待页面跳转到主页，确保登录成功
        WebDriverWait(driver, 10).until(EC.url_contains("home"))
        print("登录成功")

        # 2. 访问用户资料页面
        driver.get("http://127.0.0.1:5000/userProfile")

        # 等待用户资料页面加载
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "profile-container")))

        # 3. 验证表单数据是否正确加载（检查用户名，性别等字段）
        username_value = driver.find_element(By.ID, "username").get_attribute("value")
        assert username_value == "test_user1", f"用户名显示错误，期望 'test_user1'，但实际为 {username_value}"

        gender_value = driver.find_element(By.ID, "gender").get_attribute("value")
        assert gender_value == "alien", f"性别显示错误，期望 'Alien'，但实际为 {gender_value}"

        nickname_value = driver.find_element(By.ID, "nickname").get_attribute("value")
        assert nickname_value == "tester1", f"昵称显示错误，期望 'Tester'，但实际为 {nickname_value}"

        # 4. 修改用户资料（例如，修改昵称和性别）
        new_nickname = "NewNickname"
        driver.find_element(By.ID, "nickname").clear()  # 清除原有昵称
        driver.find_element(By.ID, "nickname").send_keys(new_nickname)  # 输入新的昵称

        # 修改性别
        gender_dropdown = driver.find_element(By.ID, "gender")
        gender_dropdown.click()  # 打开下拉菜单
        gender_dropdown.find_element(By.XPATH, "//option[@value='male']").click()  # 选择男

        # 5. 提交修改后的表单
        save_button = driver.find_element(By.CLASS_NAME, "save-btn")
        save_button.click()

        # 7. 重新加载页面，确认昵称更新成功
        driver.get("http://127.0.0.1:5000/userProfile")

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "profile-container")))
        updated_nickname_value = driver.find_element(By.ID, "nickname").get_attribute("value")
        assert updated_nickname_value == new_nickname, f"昵称更新失败，期望 '{new_nickname}'，但实际为 {updated_nickname_value}"

        print("用户资料更新成功")

        add_test_result(9, 1, "User profile updated successfully")

    except Exception as e:
        print(f"测试失败，原因: {str(e)}")
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
test_register_page()
