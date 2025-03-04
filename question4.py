from flask import Flask, request, jsonify
from datetime import datetime
from question2_3 import connect_db


app = Flask(__name__)


@app.route('/api/search-volume', methods=['POST'])
def get_search_volume():
	try:
		# Parse input json
		data = request.get_json()
		user_id = data.get('user_id')
		keywords = data.get('keywords')
		timing = data.get('timing')  # 'hourly' or 'daily'
		start_time = datetime.fromisoformat(data.get('start_time'))
		end_time = datetime.fromisoformat(data.get('end_time'))

		# check if any of input is None
		if not all([user_id, keywords, timing, start_time, end_time]):
			return jsonify({'error': 'Missing required parameters'}), 400

		if timing not in ['hourly', 'daily']:
			return jsonify({'error': 'Invalid timing parameter'}), 400
		conn = connect_db()
		cursor = conn.cursor()
		# Verify user exists and is active
		cursor.execute(
			"SELECT is_active FROM user WHERE user_id = %s", (user_id))
		user = cursor.fetchone()
		if not user or user['is_active'] == 0:
			return jsonify({'error': 'Invalid or inactive user'}), 403

		# query to ensure the requested date range is overlap subscription date range
		# requested start_date <= subscription end_date and requested end_date >= subscription start_date
		in_placeholders = ', '.join(['%s'] * len(keywords))
		subscription_query = f"""
			SELECT us.keyword_id, k.keyword_name, st.name as subscription_type
			FROM user_subscription us
			JOIN keyword k ON us.keyword_id = k.keyword_id
			JOIN subscription_types st ON us.subscription_type_id = st.subscription_type_id
			WHERE us.user_id = %s 
			AND us.start_date <= %s 
			AND us.end_date >= %s
			AND k.keyword_name IN ({in_placeholders})
		"""
		params = (user_id, end_time, start_time) + tuple(keywords)
		cursor.execute(subscription_query, params)

		subscriptions = cursor.fetchall()
		# get the list of keyword under subscription in the requested date range
		allowed_keywords = {
			sub['keyword_name']: sub['subscription_type'] for sub in subscriptions}
		# Filter requested keywords based on subscription
		valid_keywords = [kw for kw in keywords if kw in allowed_keywords]
		if not valid_keywords:
			return jsonify({'error': 'No valid subscriptions for requested keywords'}), 403

		result = {}
		for keyword in valid_keywords:
			subscription_type = allowed_keywords[keyword]

			# If requesting hourly but only has daily subscription
			if timing == 'hourly' and subscription_type == 'daily':
				continue

			if timing == 'hourly':
				# Query hourly data
				query = """
					SELECT recorded_datetime, search_volume
					FROM keyword_search_volume ksv
					JOIN keyword k ON ksv.keyword_id = k.keyword_id
					WHERE k.keyword_name = %s
					AND recorded_datetime BETWEEN %s AND %s
					ORDER BY recorded_datetime
				"""
			else:
				# Query daily snapshot
				query = """
					SELECT snapshot_datetime as recorded_datetime, search_volume
					FROM daily_keyword_snapshot dks
					JOIN keyword k ON dks.keyword_id = k.keyword_id
					WHERE k.keyword_name = %s
					AND snapshot_datetime BETWEEN %s AND %s
					ORDER BY snapshot_datetime
				"""

			cursor.execute(query, (keyword, start_time, end_time))
			data = cursor.fetchall()
			result[keyword] = [
				{
					'timestamp': row['recorded_datetime'].isoformat(),
					'volume': row['search_volume']
				} for row in data
			]

		# Close database connection
		cursor.close()
		conn.close()

		return jsonify({
			'status': 'success',
			'data': result,
			'timing': timing,
			'start_time': start_time.isoformat(),
			'end_time': end_time.isoformat()
		})
	except Exception as err:
		return jsonify({'error': f'An error occurred: {str(err)}'}), 500


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)
