from flask import Flask, request, jsonify
from datetime import datetime
from question2_3 import conn

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
		
		cursor = conn.cursor(dictionary=True)
		# Verify user exists and is active
		cursor.execute("SELECT is_active FROM user WHERE user_id = %s", (user_id,))
		user = cursor.fetchone()
		if not user or not user['is_active']:
			return jsonify({'error': 'Invalid or inactive user'}), 403
		
		## query to ensure the requested date range is overlap subscription date range
		cursor.execute("""
            SELECT us.keyword_id, k.keyword_name, st.name as subscription_type
            FROM user_subscription us
            JOIN keyword k ON us.keyword_id = k.keyword_id
            JOIN subscription_types st ON us.subscription_type_id = st.subscription_type_id
            WHERE us.user_id = %s 
            AND us.start_date <= %s 
            AND us.end_date >= %s
            AND k.keyword_name IN (%s)
        """ % ('%s', '%s', '%s', ','.join(['%s'] * len(keywords))),
        (user_id, end_time, start_time) + tuple(keywords))

		subscriptions = cursor.fetchall()
		allowed_keywords = {sub['keyword_name']: sub['subscription_type'] for sub in subscriptions}
	except:
		pass