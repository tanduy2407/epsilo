-- Table: keyword (Stores keyword metadata)
CREATE TABLE keyword (
    keyword_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    keyword_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table: keyword_search_data (Stores hourly search volume)
CREATE TABLE keyword_search_data (
    keyword_id BIGINT NOT NULL,
    created_datetime DATETIME NOT NULL,
    search_volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (keyword_id, recorded_datetime),
    FOREIGN KEY (keyword_id) REFERENCES keyword(keyword_id) ON DELETE CASCADE
);

-- Table: daily_keyword_snapshot (Store snapshot search volume in 9AM or nearest in each day)
CREATE TABLE daily_keyword_snapshot (
    snapshot_id BIGINT AUTO_INCREMENT,
    keyword_id BIGINT NOT NULL,
    snapshot_datetime DATETIME NOT NULL,
    search_volume BIGINT NOT NULL,
    recorded_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (snapshot_id),
    UNIQUE (keyword_id, recorded_date),
    FOREIGN KEY (keyword_id) REFERENCES keyword(keyword_id) ON DELETE CASCADE
);

-- Table: user (Stores user information)
CREATE TABLE user (
    user_id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
	is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table: subscription_types (Stores subscription type)
CREATE TABLE subscription_types (
    subscription_type_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,  -- 'hourly', 'daily'
    description TEXT
);

-- Insert the two subscription types
INSERT INTO subscription_types (name, description) VALUES 
('hourly', 'Access to both hourly and daily search volume data'),
('daily', 'Access to daily search volume data only');

-- Table: user_subscription (Tracks user subscriptions)
CREATE TABLE user_subscription (
    subscription_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    keyword_id BIGINT NOT NULL,
    subscription_type_id INT NOT NULL,
    start_date DATETIME NOT NULL,  -- Subscription start time
    end_date DATETIME NOT NULL,  -- Subscription end time
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES keyword(keyword_id) ON DELETE CASCADE,
	FOREIGN KEY (subscription_type_id) REFERENCES subscription_types(subscription_type_id)
);

-- Indexes for performance
CREATE INDEX idx_keyword_name ON keyword(keyword_name);
CREATE INDEX idx_recorded_datetime ON keyword_search_data(recorded_datetime);
CREATE INDEX idx_subscription ON user_subscription(user_id, keyword_id, subscription_type_id);
