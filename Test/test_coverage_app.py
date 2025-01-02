import unittest
from app import app

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
        response = self.client.post('/newRecords', data={
            'amount': 100,
            'category-level-1': 'Necessities',
            'category-level-2': 'Food',
            'date': '2024-01-01',
            'note': 'Test note'
        })
        self.assertEqual(response.status_code, 302)  # 应该重定向

if __name__ == '__main__':
    unittest.main()
