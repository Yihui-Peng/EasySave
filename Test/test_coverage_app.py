import unittest
from app import app
from unittest.mock import patch
class AppTestCase(unittest.TestCase):
    def test_example(self):
        pass
    def setUp(self):
        """配置测试环境"""
        app.testing = True
        self.client = app.test_client()

    def test_home_route(self):
        """测试 /home 路由"""
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)

    def test_login_route(self):
        """测试 /login 路由"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_data_route(self):
        """测试 /data 路由"""
        response = self.client.get('/data')
        self.assertEqual(response.status_code, 200)

    def test_new_records_post(self):
        """测试 /newRecords 路由的 POST 请求"""
        with self.client.session_transaction() as session:
            session['user_id'] = 1  # 模拟用户登录
        response = self.client.post('/newRecords', data={
            'amount': '100',
            'category-level-1': 'Necessities',
            'category-level-2': 'Food',
            'date': '2024-01-01',
            'note': 'Test note'
        })
        self.assertEqual(response.status_code, 302)

        # 测试表单字段缺失
        response = self.client.post('/newRecords', data={
            'amount': '',
            'category-level-1': 'Necessities',
            'category-level-2': '',
            'date': '',
            'note': 'Test note'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please fill out all required fields', response.data)

        # 测试数据库提交失败
        with patch('app.db.session.commit', side_effect=Exception('DB Error')):
            response = self.client.post('/newRecords', data={
                'amount': '100',
                'category-level-1': 'Necessities',
                'category-level-2': 'Food',
                'date': '2024-01-01',
                'note': 'Test note'
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'An error occurred while saving the record.', response.data)


                

    def test_saving_goal(self):
        """测试 /savingGoal 路由的 POST 请求"""
        response = self.client.post('/savingGoal', data={
            'amount': '1000',
            'start-date': '2024-01-01',
            'end-date': '2024-12-31',
            'progress': 'ongoing',
            'progress_amount': '500'
        })
        self.assertEqual(response.status_code, 200)  # 修改为预期的状态码
    def test_new_records_post_missing_data(self):
        """测试表单缺失字段的情况"""
        with self.client.session_transaction() as session:
            session['user_id'] = 1

        response = self.client.post('/newRecords', data={
            'amount': '',  # 缺少金额
            'category-level-1': 'Necessities',
            'category-level-2': 'Food',
            'date': '2024-01-01',
            'note': 'Test note'
        })

        # 检查返回状态码是否为 200（页面重新渲染）
        self.assertEqual(response.status_code, 200)
        # 检查是否显示缺少字段的错误消息
        self.assertIn(b'Please fill out all required fields', response.data)


    def test_new_records_post_db_failure(self):
        """测试数据库提交失败的情况"""
        with self.client.session_transaction() as session:
            session['user_id'] = 1  # 模拟用户登录
        with patch('app.db.session.commit', side_effect=Exception('DB Error')):
            response = self.client.post('/newRecords', data={
                'amount': '100',
                'category-level-1': 'Necessities',
                'category-level-2': 'Food',
                'date': '2024-01-01',
                'note': 'Test note'
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'An error occurred while saving the record.', response.data)
    def test_login(self):
        """测试登录功能"""
        with self.client.session_transaction() as session:
            session['user_id'] = 1  # 模拟用户登录
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('user_id', session)

    def test_register(self):
        """测试注册功能"""
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm-password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # 确保重定向到 survey
        self.assertIn('/survey', response.location)

        # 测试用户名重复
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm-password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username or email already exists', response.data)
    def test_predict(self):
        """测试 /predict 路由"""
        response = self.client.get('/predict')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Predicted Spending for Next Month', response.data)


    def test_details_and_charts(self):
        """测试 /details_and_charts 路由"""
        with self.client.session_transaction() as session:
            session['user_id'] = 1

        response = self.client.get('/details_and_charts')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Detail Records', response.data)




if __name__ == '__main__':
    unittest.main()

