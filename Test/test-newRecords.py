from flask import Flask, session
from app import app, db, User, Record
import unittest

# 创建一个继承 unittest.TestCase 的测试类
class TestNewRecords(unittest.TestCase):
    def setUp(self):
        # 配置测试环境和数据库
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_data.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            # 创建测试用户
            self.user = User(username='testuser', emailaddress='testuser@example.com', password='password')
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        # 清理数据库
        with app.app_context():
            db.drop_all()

    def test_get_newRecords_not_logged_in(self):
        # 测试未登录用户访问 newRecords
        response = self.app.get('/newRecords', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data)

    def test_get_newRecords_logged_in(self):
        # 模拟登录用户访问 newRecords 页面
        with self.app.session_transaction() as session:
            session['user_id'] = self.user.user_id

        response = self.app.get('/newRecords')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Record', response.data)

    def test_post_newRecords_missing_fields(self):
        # 模拟用户登录
        with self.app.session_transaction() as session:
            session['user_id'] = self.user.user_id

        # 提交不完整的表单（缺少必要字段）
        response = self.app.post('/newRecords', data={
            'amount': '',
            'category-level-1': 'Necessities',
            'category-level-2': 'Housing',
            'date': '2024-11-10'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please fill out all required fields', response.data)

    def test_post_newRecords_invalid_date_format(self):
        # 模拟用户登录
        with self.app.session_transaction() as session:
            session['user_id'] = self.user.user_id

        # 提交包含错误日期格式的表单
        response = self.app.post('/newRecords', data={
            'amount': '500',
            'category-level-1': 'Necessities',
            'category-level-2': 'Housing',
            'date': '10-11-2024'  # 错误的日期格式
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid date format', response.data)

    def test_post_newRecords_successful_submission(self):
        # 模拟用户登录
        with self.app.session_transaction() as session:
            session['user_id'] = self.user.user_id

        # 提交完整的表单
        response = self.app.post('/newRecords', data={
            'amount': '500',
            'category-level-1': 'Necessities',
            'category-level-2': 'Housing',
            'date': '2024-11-10',
            'note': 'Monthly rent'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New record added successfully', response.data)

        # 验证记录是否成功添加到数据库
        with app.app_context():
            record = Record.query.filter_by(user_id=self.user.user_id, amount=500).first()
            self.assertIsNotNone(record)
            self.assertEqual(record.category, 'Necessities:Housing')

# 运行测试
if __name__ == '__main__':
    unittest.main()
