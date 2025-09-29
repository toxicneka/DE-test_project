CREATE TABLE IF NOT EXISTS raw_users_by_posts (
    user_id INTEGER,
    post_id INTEGER PRIMARY KEY,
    title TEXT,
    body TEXT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS top_users_by_posts (
    user_id INTEGER PRIMARY KEY,
    posts_cnt INTEGER,
    calculated_at TIMESTAMP
);