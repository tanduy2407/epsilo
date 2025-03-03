DELIMITER //

CREATE PROCEDURE UpdateDailySnapshotNearest(IN target_date DATE)
BEGIN
    INSERT INTO daily_keyword_snapshot (keyword_id, snapshot_datetime, search_volume, recorded_date)
    WITH NearestRecords AS (
        SELECT 
            keyword_id,
            created_datetime,
            search_volume,
            ABS(TIME_TO_SEC(TIMEDIFF(created_datetime, CONCAT(target_date, ' 09:00:00')))) AS time_diff
        FROM keyword_search_data
        WHERE DATE(created_datetime) = target_date
    ),
    RankedRecords AS (
        SELECT 
            keyword_id,
            created_datetime,
            search_volume,
            ROW_NUMBER() OVER (PARTITION BY keyword_id ORDER BY time_diff) AS rn
        FROM NearestRecords
    )
    SELECT 
        keyword_id,
        created_datetime,
        search_volume,
        target_date
    FROM RankedRecords
    WHERE rn = 1
    ON DUPLICATE KEY UPDATE 
        snapshot_datetime = VALUES(snapshot_datetime),
        search_volume = VALUES(search_volume);
END //

DELIMITER ;

CALL UpdateDailySnapshotNearest('2025-03-02');