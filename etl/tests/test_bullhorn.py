import unittest
from unittest.mock import patch
from bullhorn import BullhornClient

class TestBullhornClient(unittest.TestCase):
    def setUp(self):
        self.client = BullhornClient('test_user', 'test_password', 'test_client_id', 'test_client_secret')

    @patch('login.requests.get')
    def test_get_auth_code(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.headers = {'Location': 'https://example.com?code=test_auth_code'}
        auth_code = self.client._get_auth_code('test_user', 'test_password', 'test_client_id')
        mock_get.assert_called_once_with(
            'https://auth-west.bullhornstaffing.com/oauth/authorize',
            params={
                'client_id': 'test_client_id',
                'response_type': 'code',
                'username': 'test_user',
                'password': 'test_password',
                'action': 'Login'
            },
            allow_redirects=False
        )
        self.assertEqual(auth_code, 'test_auth_code')

    @patch('login.requests.post')
    def test_get_token(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token'
        }
        auth_code = 'test_auth_code'
        self.client._get_token(auth_code)
        mock_post.assert_called_once_with(
            'https://auth-west.bullhornstaffing.com/oauth/token',
            params={
                'grant_type': 'authorization_code',
                'code': auth_code,
                'client_id': 'test_client_id',
                'client_secret': 'test_client_secret'
            }
        )
        self.assertEqual(self.client.token, 'test_access_token')
        self.assertEqual(self.client.refresh_token, 'test_refresh_token')

    @patch('login.requests.get')
    def test_authenticate(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 302
        mock_response.headers = {'Location': 'https://example.com?code=test_auth_code'}
        self.client.authenticate()
        mock_get.assert_called_once_with(
            'https://auth-west.bullhornstaffing.com/oauth/authorize',
            params={
                'client_id': 'test_client_id',
                'response_type': 'code',
                'username': 'test_user',
                'password': 'test_password',
                'action': 'Login'
            },
            allow_redirects=False
        )
        self.assertEqual(self.client.token, 'test_access_token')
        self.assertEqual(self.client.refresh_token, 'test_refresh_token')

if __name__ == '__main__':
    unittest.main()