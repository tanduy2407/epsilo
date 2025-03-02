import random
# import pymysql
# from pymysql import Connection
# from datetime import datetime, timedelta

# start_date = datetime.now() - timedelta(days=3)
# end_date = datetime.now()
# hourly_data = []
# daily_data = []


# keyword_ids = [i for i in range(1, 2)]
# current_date = start_date
# while current_date <= end_date:
#     for keyword_id in keyword_ids:
#         # Generate hourly search volume data
#         daily_records = []
#         for hour in range(24):
#             timestamp = current_date.replace(hour=hour, minute=0, second=0)
#             search_volume = random.randint(1000, 50000)
#             hourly_data.append((keyword_id, timestamp, search_volume, 'hourly'))
#             # print('hourly:', hourly_data)
#             daily_records.append((timestamp, search_volume))
#             # print('daily_records:', daily_records)

#         # Get the closest 9:00 AM record
#         nine_am_timestamp = current_date.replace(hour=9, minute=0, second=0)
#         closest_hourly_record = min(daily_records, key=lambda x: abs((x[0] - nine_am_timestamp).total_seconds()))
#         print(closest_hourly_record)
#         daily_data.append((keyword_id, nine_am_timestamp, closest_hourly_record[1], 'daily'))

#     current_date += timedelta(days=1)

hours = list(range(25))  # 0 to 24 inclusive
# Randomly shuffle the list
random.shuffle(hours)
print(hours)
# Optionally, take a subset (e.g., first 8), or use the full list
hours = hours[:random.randint(16, 22)]
hours.sort()
# print(hours)
    