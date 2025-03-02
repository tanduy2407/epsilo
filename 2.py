import random
import pymysql
from datetime import datetime, timedelta


# Connect to MySQL database
def connect_db():
    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'tanduy2407',
        'database': 'search_volume_service'
    }
    conn = pymysql.connect(**DB_CONFIG)
    return conn


# Create real-world keywords
def create_keywords(conn):
    keywords = ['iphone', 'laptop', 'crypto', 'fitness', 'tech job',
                'flights', 'stock market', 'game', 'AI chatbot', 'weather']
    with conn.cursor() as cursor:
        for kw in keywords:
            cursor.execute(
                'INSERT IGNORE INTO keyword (keyword_name) VALUES (%s)', (kw,))
        print('Inserted data successfully!')
    conn.commit()

# Create keyword volume daily
def create_keyword_volume(conn):
    start_date = datetime.now() - timedelta(days=10)
    end_date = datetime.now()
    hourly_data = []
    # daily_data = []

    # Demonstrate the list of random hour in 1 day
    hours = list(range(25))  # 0 to 24 inclusive
    random.shuffle(hours)
    hours = hours[:random.randint(16, 24)]
    hours.sort()

    with conn.cursor() as cursor:
        cursor.execute('SELECT keyword_id FROM keyword')
        keyword_ids = [row[0] for row in cursor.fetchall()]
        current_date = start_date
        # Generate hourly search volume data
        while current_date <= end_date:
            for keyword_id in keyword_ids:
                daily_records = []
                for hour in hours:
                    date_time = current_date.replace(
                        hour=hour, minute=0, second=0)
                    search_volume = random.randint(1000, 50000)
                    hourly_data.append((keyword_id, date_time, search_volume))
                    daily_records.append((date_time, search_volume))

                # Get the closest 9:00 AM record
                # nine_am_date_time = current_date.replace(hour=9, minute=0, second=0)
                # closest_hourly_record = min(daily_records, key=lambda x: abs((x[0] - nine_am_date_time).total_seconds()))
                # daily_data.append((keyword_id, nine_am_date_time, closest_hourly_record[1], 'daily'))
            current_date += timedelta(days=1)

        # Bulk Insert Data
        insert_query = '''
			INSERT INTO keyword_search_data (keyword_id, recorded_datetime, search_volume) 
			VALUES (%s, %s, %s)
		'''
        cursor.executemany(insert_query, hourly_data)
        # cursor.executemany(insert_query, daily_data)
        print('Inserted data successfully!')
    conn.commit()


if __name__ == '__main__':
    conn = connect_db()
    # create_keywords(conn)
    create_keyword_volume(conn)
