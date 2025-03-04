import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
import json
from datetime import datetime
import pytz
import question4


class TestSearchVolumeService(unittest.TestCase):
	def setUp(self):
		# Create a test Flask app
		self.app = question4.app
		self.app.config['TESTING'] = True
		self.client = self.app.test_client()
		self.ctx = self.app.app_context()
		self.ctx.push()

	def get_sample_request(self):
		return {'user_id': 1,
				'keywords': ['crypto', 'fitness'],
				'timing': 'hourly',
				'start_time': '2025-02-10T00:00:00',
				'end_time': '2025-02-28T23:59:59'}

	@patch('question4.connect_db')
	def test_successful_hourly_request(self, mock_db):
		# Mock database connection and cursor
		mock_conn = MagicMock()
		mock_cursor = MagicMock()
		mock_db.return_value = mock_conn
		mock_conn.cursor.return_value = mock_cursor

		# Mock user check
		mock_cursor.fetchone.side_effect = [
			{'is_active': True}]  # User exists and is active

		# Mock subscription check
		mock_cursor.fetchall.side_effect = [
			[{'keyword_id': 1, 'keyword_name': 'crypto',
			  'subscription_type': 'hourly'},
			 {'keyword_id': 2, 'keyword_name': 'fitness',
			  'subscription_type': 'hourly'}],

			[{'recorded_datetime': datetime(2025, 2, 25), 'search_volume': 1000},
			 {'recorded_datetime': datetime(2025, 2, 25), 'search_volume': 1200}],

			[{'recorded_datetime': datetime(2025, 2, 25), 'search_volume': 800}]]

		response = self.client.post('/api/search-volume',
									data=json.dumps(self.get_sample_request()),
									content_type='application/json')

		self.assertEqual(response.status_code, 200)
		data = json.loads(response.data)
		self.assertEqual(data['status'], 'success')
		self.assertEqual(len(data['data']['crypto']), 2)
		self.assertEqual(len(data['data']['fitness']), 1)
		self.assertEqual(data['timing'], 'hourly')

	@patch('question4.connect_db')
	def test_missing_parameters(self, mock_db):
		incomplete_request = {'user_id': 1,
							  'start_time': '2025-02-10T00:00:00',
							  'end_time': '2025-02-28T23:59:59'}  # Missing keywords and timing
		response = self.client.post('/api/search-volume',
									data=json.dumps(incomplete_request),
									content_type='application/json')

		self.assertEqual(response.status_code, 400)
		data = json.loads(response.data)
		self.assertEqual(data['error'], 'Missing required parameters')

	@patch('question4.connect_db')
	def test_invalid_timing(self, mock_db):
		request = self.get_sample_request()
		request['timing'] = 'weekly'  # Invalid timing
		response = self.client.post('/api/search-volume',
									data=json.dumps(request),
									content_type='application/json')

		self.assertEqual(response.status_code, 400)
		data = json.loads(response.data)
		self.assertEqual(data['error'], 'Invalid timing parameter')

	@patch('question4.connect_db')
	def test_invalid_datetime_format(self, mock_db):
		request = self.get_sample_request()
		request['start_time'] = 'invalid-datetime'  # Invalid datetime format

		response = self.client.post('/api/search-volume',
									data=json.dumps(request),
									content_type='application/json')

		self.assertEqual(response.status_code, 500)
		data = json.loads(response.data)
		self.assertIn('An error occurred', data['error'])

	@patch('question4.connect_db')
	def test_inactive_user(self, mock_db):
		mock_conn = MagicMock()
		mock_cursor = MagicMock()
		mock_db.return_value = mock_conn
		mock_conn.cursor.return_value = mock_cursor

		mock_cursor.fetchone.return_value = {'is_active': False}  # Inactive user

		response = self.client.post('/api/search-volume',
									data=json.dumps(self.get_sample_request()),
									content_type='application/json')

		self.assertEqual(response.status_code, 403)
		data = json.loads(response.data)
		self.assertEqual(data['error'], 'Invalid or inactive user')

	@patch('question4.connect_db')
	def test_no_subscriptions(self, mock_db):
		mock_conn = MagicMock()
		mock_cursor = MagicMock()
		mock_db.return_value = mock_conn
		mock_conn.cursor.return_value = mock_cursor

		mock_cursor.fetchone.return_value = {'is_active': True}  # Active user
		mock_cursor.fetchall.return_value = []  # No subscriptions

		response = self.client.post('/api/search-volume',
									data=json.dumps(self.get_sample_request()),
									content_type='application/json')

		self.assertEqual(response.status_code, 403)
		data = json.loads(response.data)
		self.assertEqual(
			data['error'], 'No valid subscriptions for requested keywords')

	@patch('question4.connect_db')
	def test_daily_request_success(self, mock_db):
		mock_conn = MagicMock()
		mock_cursor = MagicMock()
		mock_db.return_value = mock_conn
		mock_conn.cursor.return_value = mock_cursor

		mock_cursor.fetchone.return_value = {'is_active': True}
		mock_cursor.fetchall.side_effect = [
			[{'keyword_id': 1, 'keyword_name': 'crypto', 'subscription_type': 'daily'}],
			[{'recorded_datetime': datetime(2025, 2, 24), 'search_volume': 15000}]		]

		request = self.get_sample_request()
		request['timing'] = 'daily'
		response = self.client.post('/api/search-volume',
									data=json.dumps(request),
									content_type='application/json')

		self.assertEqual(response.status_code, 200)
		data = json.loads(response.data)
		self.assertEqual(data['status'], 'success')
		self.assertEqual(len(data['data']['crypto']), 1)
		self.assertEqual(data['timing'], 'daily')


if __name__ == '__main__':
	unittest.main()
