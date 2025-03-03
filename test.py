a = f"""
            SELECT us.keyword_id, k.keyword_name, st.name as subscription_type
            FROM user_subscription us
            JOIN keyword k ON us.keyword_id = k.keyword_id
            JOIN subscription_types st ON us.subscription_type_id = st.subscription_type_id
            WHERE us.user_id = '{}' 
            AND us.start_date <= %s 
            AND us.end_date >= %s
            AND k.keyword_name IN (%s)
        """.