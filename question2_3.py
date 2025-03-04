import random
import pymysql
import string
from datetime import datetime, timedelta


# Connect to MySQL database
def connect_db():
    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'tanduy2407',
        'database': 'keyword_search_volume',
        # enable dictionary results
        'cursorclass': pymysql.cursors.DictCursor  
    }
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as err:
        print(err)


# Create 10 real-world keywords
def generate_keywords(conn):
    keywords = ['iphone', 'laptop', 'crypto', 'fitness', 'tech job',
                'flights', 'stock market', 'game', 'AI chatbot', 'weather']
    with conn.cursor() as cursor:
        for kw in keywords:
            cursor.execute(
                'INSERT IGNORE INTO keyword (keyword_name) VALUES (%s)', (kw,))
        print('Inserted data successfully!')
    conn.commit()


# Create keyword volume with random hourly
def generate_keyword_volume_hourly(conn):
    start_date = datetime.now() - timedelta(days=10)
    end_date = datetime.now()
    hourly_data = []
    with conn.cursor() as cursor:
        cursor.execute('SELECT keyword_id FROM keyword')
        keyword_ids = [row['keyword_id'] for row in cursor.fetchall()]
        current_date = start_date
        # Generate hourly search volume data
        while current_date <= end_date:
            for keyword_id in keyword_ids:
                # Demonstrate the list of random hour in 1 day
                hours = list(range(24))
                random.shuffle(hours)
                hours = hours[:random.randint(16, 24)]
                hours.sort()

                daily_records = []
                for hour in hours:
                    date_time = current_date.replace(
                        hour=hour, minute=0, second=0)
                    search_volume = random.randint(1000, 50000)
                    hourly_data.append((keyword_id, date_time, search_volume))
                    daily_records.append((date_time, search_volume))

            current_date += timedelta(days=1)

        # Bulk Insert Data
        insert_query = '''
			INSERT INTO keyword_search_volume (keyword_id, recorded_datetime, search_volume) 
			VALUES (%s, %s, %s)
		'''
        cursor.executemany(insert_query, hourly_data)
        print('Inserted data successfully!')
    conn.commit()


# Function to generate 10 random users
def generate_random_users(conn):
    def random_string(length=8):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
    users = []
    for _ in range(10):
        username = f"user_{random_string()}"
        email = f"{username}@example.com"
        users.append((username, email))

    with conn.cursor() as cursor:
        insert_query = 'INSERT INTO user (username, email) VALUES (%s, %s)'
        cursor.executemany(insert_query, users)
        print('Inserted data successfully!')
    conn.commit()


# Function to generate random subscriptions
def generate_subscriptions(conn):
    with conn.cursor() as cursor:
        cursor.execute('SELECT user_id FROM user')
        user_ids = [row['user_id'] for row in cursor.fetchall()]
        cursor.execute('SELECT keyword_id FROM keyword')
        keyword_ids = [row['keyword_id'] for row in cursor.fetchall()]
        now = datetime.now()
        subscriptions = []
        for user_id in user_ids:
            # Each user gets 4-8 random subscriptions
            num_subs = random.randint(4, 8)
            for _ in range(num_subs):
                subscription_type_id = random.choice(
                    [1, 2])  # 1=hourly, 2=daily
                keyword_id = random.choice(keyword_ids)
                start_date = now - timedelta(days=random.randint(0, 60))
                # Subscription duration in days
                duration = random.randint(7, 60)
                end_date = start_date + timedelta(days=duration)
                subscription = (user_id, keyword_id,
                                subscription_type_id, start_date, end_date)
                subscriptions.append(subscription)

        insert_query = 'INSERT INTO user_subscription (user_id, keyword_id, subscription_type_id, start_date, end_date) VALUES (%s, %s, %s, %s, %s)'
        cursor.executemany(insert_query, subscriptions)
        print('Inserted data successfully!')
    conn.commit()


if __name__ == '__main__':
    conn = connect_db()
    # generate_keywords(conn)
    # generate_keyword_volume_hourly(conn)
    # generate_random_users(conn)
    # generate_subscriptions(conn)
    conn.close()
