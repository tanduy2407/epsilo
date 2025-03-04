# Prerequisites

Before running the tests, ensure you have the following installed:

* **Python 3.6+** : Download from [python.org](https://www.python.org/downloads/).
* **pip** : Python’s package manager (usually included with Python).
* **Git** (optional): For cloning the repository if hosted on a platform like GitHub.

# Project Structure

**question4.py**: Contains the Flask application and the **/api/search-volume** endpoint logic.

**question5.py**: Contains unit tests using **unittest** and **unittest.mock** to test the service without a real database.

These 2 file need be the same level

# Setup

Follow these steps to prepare your environment:

1. Install Dependencies
   Install the required Python packages using **pip**: pip install flask pymysql pytz

* **flask**: Web framework for the service.
* **pymysql**: MySQL driver (mocked in tests, but required by the app).

# Running the Tests

The tests are designed to run without a real database by mocking the **pymysql** connection. Follow these steps to execute them:

###### Run All Tests

From the project directory, use the following command:

```bash
python -m unittest question5.py -v
```

* **-m unittest**: Runs the **unittest** module as a script.
* **question5.py**: Specifies the test file to run.
* **-v**: Verbose mode, showing output for each test
  Example output:

`test_daily_request_success (test_app.TestSearchVolumeService) ... ok test_inactive_user (test_app.TestSearchVolumeService) ... ok test_invalid_datetime_format (test_app.TestSearchVolumeService) ... ok test_invalid_timing (test_app.TestSearchVolumeService) ... ok test_missing_parameters (test_app.TestSearchVolumeService) ... ok test_no_subscriptions (test_app.TestSearchVolumeService) ... ok test_successful_hourly_request (test_app.TestSearchVolumeService) ... ok`

###### Run a Specific Test

To run a single test (e.g., **test_successful_hourly_request**):

```bash
python -m unittest question5.TestSearchVolumeService.test_successful_hourly_request -v
```

# Test Coverage

The tests in **question5.py** cover the following cases:

1. **Successful Hourly Request** : Valid request with hourly subscriptions and data.
2. **Missing Parameters** : Request missing required fields.
3. **Invalid Timing** : Request with an invalid **timing** value (e.g., "weekly").
4. **Inactive User** : Request from an inactive user.
5. **No Subscriptions** : Request for keywords without subscriptions.
6. **Successful Daily Request** : Valid daily request with data.
7. **Invalid Datetime Format** : Request with malformed datetime strings.

# Design the database

## Overview

This database schema is designed to store and manage keyword search volume data along with user subscriptions. The system tracks search volume data on an hourly and daily basis and allows users to subscribe to specific keywords.

## Database Name

`keyword_search_volume`

## Tables

### keyword

Stores metadata about keywords.

* `keyword_id` (BIGINT, Primary Key, Auto-Increment): Unique identifier for the keyword.
* `keyword_name` (VARCHAR(255), Unique, Not Null): The actual keyword.
* `created_at` (TIMESTAMP, Default: Current Timestamp): Record creation timestamp.
* `updated_at` (TIMESTAMP, Default: Current Timestamp, Auto Update): Last update timestamp.

### keyword_search_volume

Stores the hourly search volume for each keyword.

* `keyword_id` (BIGINT, Foreign Key): References `keyword(keyword_id)`.
* `recorded_datetime` (DATETIME, Primary Key): The timestamp of the search volume recording.
* `search_volume` (BIGINT, Not Null): The recorded search volume.
* `created_at` (TIMESTAMP, Default: Current Timestamp): Record creation timestamp.
* `updated_at` (TIMESTAMP, Default: Current Timestamp, Auto Update): Last update timestamp.

### daily_keyword_snapshot

Stores daily snapshots of keyword search volume at 9 AM or the nearest available record.

* `snapshot_id` (BIGINT, Primary Key, Auto-Increment): Unique identifier for the snapshot.
* `keyword_id` (BIGINT, Foreign Key): References `keyword(keyword_id)`.
* `snapshot_datetime` (DATETIME, Not Null): The timestamp of the snapshot.
* `search_volume` (BIGINT, Not Null): The recorded search volume at the snapshot time.
* `recorded_date` (DATE, Not Null, Unique for each keyword): The date of the snapshot.
* `created_at` (TIMESTAMP, Default: Current Timestamp): Record creation timestamp.

### user

Stores user information.

* `user_id` (BIGINT, Primary Key, Auto-Increment): Unique identifier for the user.
* `username` (VARCHAR(100), Unique, Not Null): The username.
* `email` (VARCHAR(255), Unique, Not Null): The user's email address.
* `is_active` (BOOLEAN, Default: TRUE, Not Null): Status of the user.
* `created_at` (TIMESTAMP, Default: Current Timestamp): Record creation timestamp.
* `updated_at` (TIMESTAMP, Default: Current Timestamp, Auto Update): Last update timestamp.

### subscription_types

Stores different types of subscriptions available for users.

* `subscription_type_id` (INT, Primary Key, Auto-Increment): Unique identifier for the subscription type.
* `name` (VARCHAR(50), Unique, Not Null): Subscription name (`hourly`, `daily`).
* `description` (TEXT): Description of the subscription type.

**Subscription Types:**

* `hourly`: Access to both hourly and daily search volume data.
* `daily`: Access to daily search volume data only.

### user_subscription

Tracks user subscriptions to specific keywords.

* `subscription_id` (BIGINT, Primary Key, Auto-Increment): Unique identifier for the subscription.
* `user_id` (BIGINT, Foreign Key): References `user(user_id)`.
* `keyword_id` (BIGINT, Foreign Key): References `keyword(keyword_id)`.
* `subscription_type_id` (INT, Foreign Key): References `subscription_types(subscription_type_id)`.
* `start_date` (DATETIME, Not Null): Subscription start timestamp.
* `end_date` (DATETIME, Not Null): Subscription end timestamp.
* `created_at` (TIMESTAMP, Default: Current Timestamp): Record creation timestamp.
* `updated_at` (TIMESTAMP, Default: Current Timestamp, Auto Update): Last update timestamp.

## Indexes for Performance

* `idx_keyword_name` on `keyword(keyword_name)`: Optimizes keyword lookups.
* `idx_recorded_datetime` on `keyword_search_volume(recorded_datetime)`: Speeds up search volume queries.
* `idx_subscription` on `user_subscription(user_id, keyword_id, subscription_type_id)`: Optimizes subscription-related queries.

## Relationships

* `keyword_search_volume` and `daily_keyword_snapshot` reference `keyword`.
* `user_subscription` references `user`, `keyword`, and `subscription_types`.
* `subscription_types` defines the available subscription levels.
