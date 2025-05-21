import unittest
import json
from app import app
from config import ADMIN_API_KEYS

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.admin_api_key = ADMIN_API_KEYS[0] if ADMIN_API_KEYS else "test_admin_key"
        self.test_api_key = "test_api_key"

    def test_get_stock_analysis(self):
        """Test stock analysis endpoint"""
        response = self.app.get(
            '/analysis/AAPL',
            headers={'X-API-Key': self.test_api_key}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('short_term', data['data'])

    def test_get_user_info(self):
        """Test user info endpoint"""
        response = self.app.get(
            '/user/info',
            headers={'X-API-Key': self.test_api_key}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)

    def test_reset_api_key(self):
        """Test API key reset endpoint"""
        response = self.app.post(
            '/user/reset-api-key',
            headers={'X-API-Key': self.test_api_key}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('api_key', data['data'])

    def test_create_user(self):
        """Test user creation endpoint"""
        test_user = {
            'name': 'Test User',
            'email': 'test@example.com',
            'plan': 'free'
        }
        response = self.app.post(
            '/admin/create_user',
            headers={'Authorization': f'Bearer {self.admin_api_key}'},
            json=test_user
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('user_id', data['data'])

    def test_list_users(self):
        """Test list users endpoint"""
        response = self.app.get(
            '/admin/users',
            headers={'Authorization': f'Bearer {self.admin_api_key}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)

if __name__ == '__main__':
    unittest.main() 